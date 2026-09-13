from django.contrib import admin
from .models import MyUser, Post
# Register your models here.
admin.site.register(MyUser)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
  list_display = ('author', 'created_at')
  search_fields = ('author__username', 'caption')