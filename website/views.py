from typing import Dict

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import HttpResponseRedirect, redirect, render, reverse
from django.views.generic import DetailView, TemplateView, UpdateView

from authentication.mixins import GrafeasStaffRequired
from website.forms import AddUserForm, PostAddForm
from website.helpers import get_additional_context
from website.models import Post


def index(request: HttpRequest) -> HttpResponse:
    """Build and render the homepage for the website."""
    context = {
        "posts": Post.objects.filter(
            published=True,
            standalone_section=False,
            show_in_news_view=True,
            engineeringblogpost=False,
        ).order_by("-date")
    }
    context = get_additional_context(context)
    return render(request, "website/index.html", context)


class PostDetail(DetailView):
    """Render a specific post on the website."""

    model = Post
    template_name = "website/post_detail.html"

    def get_context_data(self, **kwargs: object) -> Dict:
        """Build the context dict with extra data needed for the templates."""
        context = super().get_context_data(**kwargs)
        context = get_additional_context(context)
        return context


def post_view_redirect(request: HttpRequest, pk: int, slug: str) -> HttpResponse:
    """Compatibility layer to take in old-style PK+slug urls and return slug only."""
    return HttpResponseRedirect(reverse("post_detail", kwargs={"slug": slug}))


class PostUpdate(GrafeasStaffRequired, UpdateView):
    """Modify a post on the website."""

    model = Post
    fields = [
        "title",
        "body",
        "published",
        "standalone_section",
        "header_order",
        "engineeringblogpost",
    ]
    template_name = "website/generic_form.html"

    def get_context_data(self, **kwargs: object) -> Dict:
        """Build the context dict with extra data needed for the templates."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "enable_trumbowyg": True,
                # id of html element we want to convert
                "trumbowyg_target": "id_body",
                "fullwidth_view": True,
            }
        )
        context = get_additional_context(context)
        return context


class PostAdd(GrafeasStaffRequired, TemplateView):
    def get(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        """
        Build and render the page for adding a new post.

        This applies to both main site and the engineering blog.
        """
        context = {
            "form": PostAddForm(),
            "header": "Add a new post!",
            "subheader": (
                'Remember to toggle "Published" if you want your post to appear!'
            ),
            # enable the WYSIWYG editor
            "enable_trumbowyg": True,
            # id of html element we want to attach the trumbowyg to
            "trumbowyg_target": "id_body",
            "fullwidth_view": True,
        }
        context = get_additional_context(context)
        return render(request, "website/generic_form.html", context)

    def post(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        """Save a new blog post when a POST request is sent to the server."""
        form = PostAddForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return HttpResponseRedirect(f"{new_post.get_absolute_url()}edit")


class AdminView(GrafeasStaffRequired, TemplateView):
    def get(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        """Render the admin view."""
        context = {"posts": Post.objects.all(), "fullwidth_view": True}
        context = get_additional_context(context)
        return render(request, "website/admin.html", context)


# superadmin role
@staff_member_required
def user_create(request: HttpRequest) -> HttpResponse:
    """Render the user creation view."""
    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("homepage")

    else:
        form = AddUserForm()

    context = {"form": form, "header": "Create New User", "fullwidth_view": True}

    return render(request, "website/generic_form.html", context)
