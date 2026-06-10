from rest_framework import serializers
from .models import Project, Like, Comment, Bookmark, Technology
from users.serializers import UserSerializer


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ["id", "name"]


class ProjectSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    bookmarks_count = serializers.IntegerField(source="bookmarks.count", read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    tech_stack = TechnologySerializer(many=True, read_only=True)
    tech_names = serializers.SlugRelatedField(
        many=True,
        queryset=Technology.objects.all(),
        slug_field="name",
        write_only=True,
        source="tech_stack",
    )
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail', 
            'demo_url', 'source_code_url', 'tech_stack', "tech_names", 
            'is_published', 'is_liked', 'created_at', 
            'likes_count', 'comments_count', "bookmarks_count", 'view_count',
            "is_bookmarked",
            'author',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'author',
                            "view_count"]
    
    def create(self, validated_data):
        user = self.context["request"].user
        tech_stack = validated_data.pop("tech_stack", [])
        
        project = Project.objects.create(author=user, **validated_data)
        project.tech_stack.set(tech_stack)
        return project
    
    def update(self, instance, validated_data):
        tech_stack = validated_data.pop("tech_stack", None)
        instance = super().update(instance, validated_data)
        
        if tech_stack is not None:
            instance.tech_stack.set(tech_stack)
        return instance
    
    def get_is_bookmarked(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Bookmark.objects.filter(user=user, project=obj).exists()
        return False

    def get_is_liked(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Like.objects.filter(user=user, project=obj).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Menampilkan username saja

    class Meta:
        model = Comment
        fields = ['id', 'user', 'project', 'content', 'created_at']
        read_only_fields = ["user", "project", "id", "created_at"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'project']
