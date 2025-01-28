from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment, Category

# Custom User Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email")
    filter_horizontal = ("watchlist",)

# Admin for Auction Listings
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "starting_bid", "current_price", "is_active", "created_at")
    list_filter = ("is_active", "categories", "created_at")
    search_fields = ("title", "description", "owner__username")
    filter_horizontal = ("categories",)

# Admin for Categories
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

# Admin for Bids
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "auction", "amount", "timestamp")
    list_filter = ("auction", "timestamp")
    search_fields = ("bidder__username", "auction__title")

# Admin for Comments
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "auction", "content", "created_at")
    list_filter = ("auction", "created_at")
    search_fields = ("author__username", "auction__title", "content")

# Registering Models with their Admin Classes
admin.site.register(User, UserAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
