from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from mainapp.views import index, products

if settings.DEBUG:
    import debug_toolbar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('products/', include('mainapp.urls', namespace='mainapp')),
    path('users/', include('authapp.urls', namespace='authapp')),
    path('baskets/', include('baskets.urls', namespace='baskets')),
    path('admins/', include('admins.urls', namespace='admins')),
    path('', include('social_django.urls', namespace="social")),
    path('orders/', include('ordersapp.urls', namespace='orders')),
    # path('language_new/', include('django.conf.urls',namespace='language_new')),
    # path('lang/', set_language, name='language'),
    # path(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^i18n/', include('django.conf.urls.i18n')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += [path('debug/', include(debug_toolbar.urls))]
