# 📺 HLS Viewer & Navigation System

A modular web application component for viewing HLS video streams with persistent URL management and an interactive navigation interface. Features a dynamic sidebar with smooth gooey-effect navigation for seamless tool switching.

> **Note:** This is part of a larger unified tools application developed for our Software Engineering course project.

**Key Features**:
- ✅ **Stream Management** - Add, remove, and select from saved HLS streams
- ✅ **Persistent Storage** - Stream URLs saved in SQLite database
- ✅ **Gooey-Effect Navigation** - Smooth, interactive sidebar navigation
- ✅ **Responsive Design** - Works across different screen sizes
- ✅ **Real-time Video Playback** - Direct HLS stream integration

---

## 📖 Overview

The HLS Viewer component replaces previously separate video stream pages with a unified interface that allows users to manage and view multiple HLS streams. Combined with a custom navigation system featuring gooey-effect transitions, it provides an intuitive way to access all tools within the unified application.

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Backend (Django)
pip install django djangorestframework django-cors-headers

# Frontend
# HTML/CSS/JavaScript with HLS.js library
```
### 2. Running the Application
```bash
# Start Django server
python manage.py runserver

# Access the application at:
# http://localhost:8000
```
### 3. Using the HLS Viewer
1. **Access the Tool**: Click "HLS Viewer" in the navigation sidebar
2. **Add Stream**: Use the "+" button to add new stream URLs
3. **Select Stream**: Choose from dropdown of saved streams
4. **View Stream**: Video automatically loads and plays selected stream

---

## 🛠️ Technical Implementation

### Backend (Django REST Framework)
```python
# Models
class Stream(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

# API Views
class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
```
### Frontend Components

- **Navigation**: Custom gooey-effect sidebar with smooth transitions
- **HLS Player**: Video.js with HLS.js integration for stream playback
- **Stream Management**: Dynamic form for adding/removing streams

---

## 👨🏻‍💻 Project Management

### Priority System:
Since the Priority field is unavailable in our Jira setup, we use:
- **Story Points Reference**:
    - 3 points: Small, well-understood task (~1-2 days)
    - 5 points: Medium complexity (~3-4 days)
    - 8 points: Complex with some unknowns (~5-6 days)
    - 13 points: Very complex, significant unknowns (~1.5-2 weeks)
  Total Project Estimate: 99 points
- **Priority Legend**:
    - 🔴 Critical - Must be completed for project success, core functionality
    - 🟡 High - Important features that deliver significant value
    - 🟢 Medium - Valuable enhancements but not blocking core functionality

### Scrum Tools:

- Jira for backlog management and sprint tracking
- GitHub for version control with feature branches
- Daily stand-ups for team synchronization

---

## 🎨 Navigation Features

- **Gooey Effect**: Smooth blob animation during navigation
- **Tool Grouping**: Logical organization of related tools
- **Responsive Design**: Collapsible sidebar for mobile devices
- **Active State**: Visual indicators for current tool

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|---------|-----------|---------|
| GET | /api/streams/	| List all saved streams |
| POST | /api/streams/ | Add new stream |
| PUT | /api/streams/{id}/ | Update stream |
| DELETE | /api/streams/{id}/ | Remove stream |

---

## 👤 Development Team

**Team Members**:
- [Aleeza Rizwan](https://github.com/its-aleezA)
- [Shaheer Afzal](https://github.com/ShaheerAfzal)
- [Ibrahim Abdullah](https://github.com/Ibrahim5570)
- [Ayesha Majid](https://github.com/ayeshamajid3)

---

_Disclaimer: For educational purposes as part of our Software Engineering course._
