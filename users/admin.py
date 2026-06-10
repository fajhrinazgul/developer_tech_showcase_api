from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow, EmailActivation

admin.site.register(EmailActivation)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Menentukan field yang muncul di list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
    # Menentukan field mana yang bisa diklik untuk masuk ke edit view
    list_display_links = ('username', 'email')
    
    # Pengaturan field di halaman edit
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar', 'github_url')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )
    
    # Menampilkan filter di sebelah kanan
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Menambahkan fitur pencarian
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    ordering = ('username',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    
    # Memudahkan pencarian user dengan fitur autocomplete agar tidak drop-down panjang
    autocomplete_fields = ('follower', 'following')
