from django.contrib import admin
from .models import Technology, Project, Like, Comment, Bookmark

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'view_count', 'created_at')
    list_filter = ('is_published', 'created_at', 'tech_stack')
    search_fields = ('title', 'author__username')
    readonly_fields = ('slug', 'view_count', 'created_at', 'updated_at')
    filter_horizontal = ('tech_stack',)  # Memberikan UI dua kolom untuk ManyToMany
    inlines = [CommentInline]            # Melihat komentar langsung di halaman proyek
    
    # Menggunakan raw_id_fields agar tidak ada dropdown User yang sangat panjang
    raw_id_fields = ('author',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'project')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at', 'short_content')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'project')

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'project')