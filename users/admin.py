from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Entry

# Personalizar el modelo de usuario en el admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

# Registrar el modelo CustomUser
admin.site.register(CustomUser, CustomUserAdmin)

# Registrar el modelo Entry
class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email',)  # Permite buscar por el email del usuario

admin.site.register(Entry, EntryAdmin)
