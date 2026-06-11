from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F, Q
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project, Like, Comment, Bookmark, ProjectView
from .serializers import ProjectSerializer, CommentSerializer
from .permissions import IsOwnerOrAdminOrReadOnly, IsOwnerOrCommenterReadOnly
from .filters import ProjectFilter


class ProjectPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ProjectPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter
    
    def get_queryset(self):
        user = self.request.user
        is_published_param = self.request.query_params.get('is_published')
        author_param = self.request.query_params.get("author")

        # Logika: Jika user meminta filter draft (is_published=False)
        if is_published_param and is_published_param.lower() == 'false':
            if user.is_authenticated:
                # Hanya tampilkan project milik user tersebut yang draft
                return Project.objects.filter(author=user, is_published=False)
            else:
                # Jika user belum login, kembalikan queryset kosong
                return Project.objects.filter(author=user, is_published=True)
        
        if author_param:
            if user.is_authenticated:
                # Only admin or author can access
                if user.username == author_param or user.is_superuser:
                    return Project.objects.filter(author__username=author_param)
                else:
                    return Project.objects.filter(author__username=author_param, is_published=True)
            else:
                return Project.objects.filter(author__username=author_param, is_published=True)

        if user.is_authenticated:
            return Project.objects.filter(Q(is_published=True) | Q(author=user))
        else:
            return Project.objects.filter(is_published=True)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    
    def get_object(self):
        obj = super().get_object()
        # Hanya hitung jika user sudah login
        if self.request.user.is_authenticated:
            # Coba buat record view baru (Atomic operation)
            # Jika record sudah ada (karena unique_together), tidak akan error, hanya tidak dibuat
            _, created = ProjectView.objects.get_or_create(
                user=self.request.user, 
                project=obj
            )
            
            # Jika record baru berhasil dibuat (artinya pertama kali lihat), update view_count
            if created:
                obj.view_count += 1
                obj.save(update_fields=['view_count'])
        
        return obj


class ProjectBookmarkToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        project = generics.get_object_or_404(Project, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, project=project)
        if not created:
            bookmark.delete()
            return Response({"status": "bookmark removed"}, status=status.HTTP_200_OK)
        return Response({"status": "bookmark added"}, status=status.HTTP_201_CREATED)


class UserBookmarkListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(bookmarks__user=self.request.user)


class ProjectLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        project = generics.get_object_or_404(Project, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, project=project)
        if not created:
            like.delete()
            return Response({'status': 'unliked'})
        return Response({'status': 'liked'})


class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ProjectPagination

    def get_queryset(self):
        return Comment.objects.filter(project_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        project = generics.get_object_or_404(Project, pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, project=project)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrCommenterReadOnly]
    
    def get_object(self):
        project_id = self.kwargs["project_id"]
        comment_id = self.kwargs["comment_id"]
        comment = generics.get_object_or_404(Comment,  pk=comment_id, project_id=project_id)
        self.check_object_permissions(self.request, comment)
        return comment