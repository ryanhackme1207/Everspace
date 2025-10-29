# EverSpace - Modern Real-Time Chat Application

A sophisticated real-time chat application built with Django 5.2, WebSockets, and modern UI/UX design principles.

## 🚀 Features

### ✨ Modern Design
- **Glass Morphism UI** - Beautiful transparent glass effects with backdrop filters
- **Bootstrap 5.3.2** - Latest responsive framework for modern layouts
- **Custom SVG Icons** - Unique vector graphics and animations
- **Particle Animations** - Dynamic floating particles background
- **Gradient Themes** - Stunning color gradients throughout the interface

### 🔐 Advanced Security
- **Multi-Factor Authentication (MFA)** - TOTP-based two-factor authentication
- **Backup Codes** - Emergency access codes for account recovery
- **Admin Recovery System** - Administrative MFA recovery management
- **Session Security** - Secure session handling and CSRF protection

### 💬 Real-Time Chat Features
- **WebSocket Connections** - Instant message delivery using Django Channels
- **Active User Tracking** - See who's online in real-time
- **Join/Leave Notifications** - Smart anti-spam system for user activity
- **Multiple Rooms** - Create and join different chat rooms
- **Message History** - Persistent message storage and retrieval

### 🛠️ Technical Excellence
- **Django 5.2.7** - Latest Django framework with async support
- **ASGI Support** - Modern asynchronous server gateway interface
- **Redis/InMemory Channels** - Scalable WebSocket message routing
- **Responsive Design** - Mobile-first approach with modern CSS

## 🏗️ Technology Stack

- **Backend**: Django 5.2.7, Django Channels, django-otp
- **Frontend**: Bootstrap 5.3.2, Font Awesome 6.4.0, Custom CSS/JS
- **WebSockets**: Django Channels with Daphne ASGI server
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django Auth + TOTP MFA
- **Fonts**: Google Fonts (Inter, Space Grotesk)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/ryanhackme1207/Everspace.git
   cd Everspace
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django==5.2.7
   pip install channels
   pip install channels-redis
   pip install django-otp
   pip install daphne
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**
   ```bash
   # For development with WebSocket support
   python -m daphne -b 127.0.0.1 -p 8000 discord_chat.asgi:application
   
   # Or regular Django server (limited WebSocket support)
   python manage.py runserver
   ```

## 🎯 Usage

1. **Access the application** at `http://127.0.0.1:8000/`
2. **Register a new account** or login with existing credentials
3. **Set up MFA** (optional but recommended) from user settings
4. **Join chat rooms** and start real-time conversations
5. **Create new rooms** by typing a room name and joining

## 🎨 Design Features

- **Glass Morphism Effects**: Translucent elements with blur effects
- **Particle Animation System**: Floating particles for visual appeal
- **Responsive Grid Layouts**: Modern CSS Grid and Flexbox
- **Custom SVG Graphics**: Scalable vector icons and decorations
- **Smooth Animations**: CSS transitions and keyframe animations

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=your-database-url
```

### WebSocket Configuration
The application uses Django Channels for WebSocket support:
- Development: InMemoryChannelLayer
- Production: Redis-backed channel layer (recommended)

## 📱 Mobile Support

EverSpace is fully responsive and optimized for:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Desktop (1024px+)
- 🖥️ Large screens (1440px+)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Team** for the excellent web framework
- **Bootstrap Team** for the responsive CSS framework
- **Font Awesome** for the icon library
- **Google Fonts** for typography

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the Django documentation
- Review the Django Channels documentation

---

**Built with ❤️ by Ryan Lai**

*EverSpace - Where conversations come alive in real-time*