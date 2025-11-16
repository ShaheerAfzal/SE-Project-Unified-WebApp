# models.py
import re
from io import BytesIO
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile


# Optional: if you use docxtpl for templating
# pip install docxtpl
try:
    from docxtpl import DocxTemplate
    DOCXTPL_AVAILABLE = True
except Exception:
    DOCXTPL_AVAILABLE = False
    
# Create your models here.

# helper: extract placeholders in two common formats:
# [FIELD_NAME] and {{FIELD_NAME}}  (keeps the raw key names)
def extract_placeholders_from_docx(path_or_file):
    """
    Accepts a file path or a file-like object for a .docx file.
    Returns a sorted list of unique placeholder keys (strings).
    Supports [KEY], {{KEY}} and other bracketed forms.
    """
    # Use python-docx to read document text (safe minimal dependency)
    # pip install python-docx
    from docx import Document

    # Load document
    if hasattr(path_or_file, "read"):
        doc = Document(path_or_file)
    else:
        doc = Document(path_or_file)

    text = []
    for p in doc.paragraphs:
        text.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text.append(cell.text)
    joined = "\n".join(text)

    keys = set()

    # patterns: [KEY], {{KEY}}, allow spaces inside then strip
    for m in re.findall(r"\[([^\]]+)\]", joined):
        keys.add(m.strip())
    for m in re.findall(r"\{\{([^}]+)\}\}", joined):
        keys.add(m.strip())

    # normalize keys to uppercase and replace spaces with underscores (optional)
    normalized = []
    for k in keys:
        nk = k.strip()
        # keep original if already looks like a safe key (letters, digits, underscore)
        # else convert spaces -> underscore
        nk = re.sub(r"\s+", "_", nk)
        normalized.append(nk)

    return sorted(set(normalized))


class DocumentTemplate(models.Model):
    """
    Stores an uploaded .docx template and its extracted field definitions.
    `fields` stores a mapping of placeholder_key -> friendly_label (optional).
      Example: {"PRODUCT_NAME": "Product Name", "QUANTITY": "Quantity"}
    `key_field` is one of the placeholder keys used as the primary identifier for documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="doc_templates/")
    fields = models.JSONField(default=dict, blank=True)
    key_field = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def extract_and_populate_fields(self):
        """
        Extract placeholders from the docx file and populate self.fields
        if fields is empty or if the file changed.
        Uses the `extract_placeholders_from_docx` helper.
        Friendly labels default to a humanized version of the key.
        """
        # open underlying file for reading
        f = self.file
        f.open(mode="rb")
        try:
            keys = extract_placeholders_from_docx(f)
        finally:
            f.close()

        # build mapping key -> friendly label
        mapping = {}
        for k in keys:
            # humanize: replace underscores with spaces, title-case
            label = k.replace("_", " ").strip().title()
            mapping[k] = label

        self.fields = mapping
        # set a sensible default key_field if not set
        if not self.key_field and keys:
            self.key_field = keys[0]
        self.save(update_fields=["fields", "key_field", "updated_at"])

    def generate_filled_docx_bytes(self, field_values: dict):
        """
        Generate a .docx bytes object by replacing placeholders with field_values.
        This uses docxtpl if available, otherwise a simple python-docx replace.
        Returns a BytesIO containing the generated .docx file.
        """
        if DOCXTPL_AVAILABLE:
            # docxtpl supports Jinja-like placeholders; ensure template uses {{ KEY }} style
            tpl = DocxTemplate(self.file.path if hasattr(self.file, "path") else self.file)
            # docxtpl expects keys as simple mapping
            ctx = {k: field_values.get(k, "") for k in self.fields.keys()}
            tpl.render(ctx)
            out = BytesIO()
            tpl.save(out)
            out.seek(0)
            return out
        else:
            # Fallback: naive replace in paragraphs and table cells using python-docx
            from docx import Document
            if hasattr(self.file, "path"):
                doc = Document(self.file.path)
            else:
                # file-like object: need to re-open
                doc = Document(self.file)

            def replace_in_paragraphs(paragraphs):
                for p in paragraphs:
                    inline = p.runs
                    if not inline:
                        continue
                    fulltext = "".join([r.text for r in inline])
                    newtext = fulltext
                    for key in self.fields.keys():
                        # support replacement in both formats
                        newtext = newtext.replace(f"[{key}]", str(field_values.get(key, "")))
                        newtext = newtext.replace(f"{{{{{key}}}}}", str(field_values.get(key, "")))
                    if newtext != fulltext:
                        # replace whole run set with one run to avoid run fragmentation handling complexities
                        for i in range(len(inline)-1, -1, -1):
                            p.runs[i].text = ""
                        p.add_run(newtext)

            replace_in_paragraphs(doc.paragraphs)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        replace_in_paragraphs(cell.paragraphs)

            out = BytesIO()
            doc.save(out)
            out.seek(0)
            return out


class GeneratedDocument(models.Model):
    """
    Stores a record of a generated document (but not necessarily the binary file).
    field_values: the data used to fill the template so the doc can be regenerated.
    If you want to store the generated binary file, you can add an optional FileField.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, related_name="documents")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    field_values = models.JSONField()  # mapping key -> value
    key_field_value = models.CharField(max_length=255, blank=True, null=True)
    # optionally store the generated file (commented out)
    # file = models.FileField(upload_to="generated/", null=True, blank=True)

    def __str__(self):
        return f"{self.template.name} - {self.key_field_value or self.created_at.isoformat()}"

    def generate_and_attach_file(self):
        """
        Generate .docx bytes and optionally save to self.file if you enabled it.
        Returns a BytesIO of the generated docx.
        """
        out = self.template.generate_filled_docx_bytes(self.field_values)
        # If you want to attach/save the generated file:
        # filename = f"{self.template.name}_{self.key_field_value or timezone.now().strftime('%Y%m%d%H%M%S')}.docx"
        # self.file.save(filename, ContentFile(out.read()), save=True)
        out.seek(0)
        return out