from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'row': 3, 'col': 10}),
        }


class PostSearchForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('district', 'subject', 'class_level',)
