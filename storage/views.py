from django.http import HttpResponse
from api_rackian import settings
from rest_framework import viewsets, views
from rest_framework.response import Response
from storage.models import Folder, File
from storage.serializers import FolderSerializer, FileSerializer
from rest_framework import authentication, permissions, parsers, status
import mimetypes


class FolderViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for listing or retrieving Folders.
    """
    serializer_class = FolderSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)


class FileViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing or retrieving Files.
    """
    serializer_class = FileSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.MultiPartParser,)

    def get_queryset(self):
        files = File.objects.filter(user=self.request.user)
        folder = self.request.query_params.get('folder', None)
        if folder is not None:
            if folder != '':
                files = files.filter(folder=folder)
            else:
                files = files.filter(folder=None)
        return files

    @staticmethod
    def max_space(request):
        # 100MB
        return 104857600

    @staticmethod
    def have_space(request):
        max_space = FileViewSet.max_space(request)
        space = request.user.space
        file_space = request.data['link'].size
        return (space + file_space) <= max_space

    def create(self, request, *args, **kwargs):
        if not FileViewSet.have_space(self.request):
            data = {'error': 'Not enough space'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        user.space = user.space + request.data['link'].size
        user.save()
        return super(FileViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        user.space = user.space - self.get_object().size
        if user.space < 0:
            user.space = 0
        user.save()
        return super(FileViewSet, self).destroy(request, *args, **kwargs)


class DownloadableFileView(views.APIView):
    """
    A View for download Files.
    """
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)

    def get(self, request, id):
        """
        Download file.
        """
        real_path = settings.STORAGE_FOLDER_ABS + '/' + id

        try:
            user = self.request.user
            complete_path = settings.STORAGE_FOLDER + '/' + id
            print complete_path
            file = File.objects.filter(user=user, id=id).first()
            fp = open(real_path, 'rb')
            response = HttpResponse(fp.read(), content_type=file.mime_type)
            response['Content-Length'] = fp.tell()
            fp.close()
            mime = mimetypes.guess_extension(file.mime_type)
            if mime == '.jpe':
                mime = '.jpg'
            response['Content-Disposition'] = 'attachment; filename=' + file.name + mime
        except:
            return Response('not exists')
        return response