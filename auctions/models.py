from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# Custom User Model
class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', blank=True, related_name="watchers")
    def __str__(self):
        return self.username

# Model for Auction Listings
class AuctionListing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=200, null=True, blank=True)
    categories = models.ManyToManyField('Category', related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    winning_bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def save(self, *args, **kwargs):
        # Ensure current_price is the same as starting_bid if it's not already set
        if not self.current_price:
            self.current_price = self.starting_bid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Model for Bids
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"

# Model for Comments
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500)  # Optional character limit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest comments first

    def __str__(self):
        return f"Comment by {self.author} on {self.auction} at {self.created_at}"
