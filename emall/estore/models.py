from django.db import models
from django import forms

from wagtail.snippets.models import register_snippet

#added imports for parentalkey, orderable, inlinepanel, imagechooserpanel,

from modelcluster.fields import ParentalKey,ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank = True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname = "full")
    ]

    def get_context(self, request):
        #update context to include only published posts, ordered by reverse
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('first_published_at')
        context['blogpages'] = blogpages
        return context
        
        pass
    pass

class BlogTagIndexPage(Page):
    def get_context(self, request):

        #filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.object.filter(tags_name = tag)

        #updated template context
        conext = super().get_context(request)
        conext['blogpages'] = blogpages
        return context

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name = 'tagged_items',
        on_delete = models.CASCADE,
    )

class  BlogPage(Page):
    date = models.DateField('Post date')
    intro = models.CharField(max_length = 250)
    body = RichTextField(blank = True)
    tags = ClusterTaggableManager(through = BlogPageTag, blank = True)
    categories = ParentalManyToManyField('estore.BlogCategory', blank = True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget = forms.CheckboxSelectMultiple),
        ], heading = 'Blog Information'),
        #FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname = 'full'),
        InlinePanel('gallery_images', label = 'Gallery images'),
        
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete = models.CASCADE, related_name = 'gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete = models.CASCADE, related_name = '+'
    )
    caption = models.CharField(blank = True, max_length = 250)

    panels = [
        ImageChooserPanel( 'image'),
        FieldPanel('caption'),
    ]
 
class StoreIndexPage(Page):
    intro = RichTextField(blank = True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = [
        'estore.CategoryIndexPage',
        'estore.ProductIndexPage',

    ]

    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        return context

    pass

class CategoryIndexPage(Page):

    max_count = 1
    
    subpage_types = [
        'estore.Category',
    ]


class Category(Page):

    subpage_types = []

    class Meta:
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'
 
class ProductIndexPage(Page):
    
    max_count = 1
    
    subpage_types = [
        'estore.Product',
    ]


class Product(Page):
    product_category = models.ForeignKey(
        to = 'estore.Category',
        related_name= 'products',
        on_delete = models.PROTECT,
    )
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete = models.SET_NULL, null = True, 
    )
    description = RichTextField(blank = True)
    price = models.DecimalField(max_digits=10, decimal_places= 2)
    available = models.BooleanField(default= True)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname = 'full'),
        FieldPanel('product_category', classname = 'full'),
        FieldPanel('price', classname = 'full'),
        FieldPanel('available', classname = 'full'),
        ImageChooserPanel('image'),
    ]    

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length = 255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null = True, blank = True,
        on_delete= models.SET_NULL, related_name='+',
        )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon')
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'category'
        verbose_name_plural = 'categories'