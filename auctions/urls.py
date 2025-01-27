from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<int:listing_id>",views.add_to_watchlist, name="add_to_watchlist"),
    path("rem_from_watchlist/<int:listing_id>",views.rem_from_watchlist, name="rem_from_watchlist"),
    path("add_comment/<int:listing_id>",views.add_comment, name="add_comment"),
    path("close_listing/<int:listing_id>",views.close_listing, name="close_listing"),
    path("open_listing/<int:listing_id>",views.open_listing, name="open_listing"),
    path("place_bid/<int:listing_id>",views.place_bid, name="place_bid"),
    path("categories",views.categories, name="categories"),
    path("category/<str:category_name>",views.category, name="category"),
]
