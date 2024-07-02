
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webservermaintenance/', include('webserverMaintenance.urls')),  # Include URLs from the 'main' app
    path('sites/', include('sites.urls')),
    path('oraclequery/', include('oracleQuery.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', include('MainApp.urls')),
    path('audit_queries/', include('audit_queries.urls')),
    path('serverlogs/', include('serverLogs.urls')),
    path('timezone_updater/', include('timezone_updater.urls')),
    path('unscramble_mac/', include('pacsscan.urls')),
    path('ei_status/', include('ei_status.urls')),
]