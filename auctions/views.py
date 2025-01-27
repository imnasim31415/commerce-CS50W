from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User, AuctionListing,Comment,Bid,Category

def category(request, category_name):
    category = Category.objects.get(name=category_name)
    listings = category.listings.all()
    return render(request, "auctions/category.html",{
        'category': category,
        'listings': listings
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html",{
        'categories': categories
    })

def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        try:
            bid_amount = float(request.POST["bid_amount"])
        except ValueError:
            messages.error(request, "Invalid bid amount.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        
        if bid_amount <= listing.current_price:
            messages.error(request, "Bid amount must be greater than the current price.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        
        # Create the bid
        bid = Bid(
            bidder=request.user,
            auction=listing,
            amount=bid_amount
        )
        bid.save()

        listing.current_price = bid_amount
        listing.winning_bidder = request.user
        listing.save()


        messages.success(request, "Bid has been placed successfully.")
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def open_listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user == listing.owner:
        listing.is_active = True
        listing.save()
        messages.success(request, "Listing has been opened.")
    else:
        messages.error(request, "You are not the owner of this listing.")
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def close_listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user == listing.owner:
        listing.is_active = False
        listing.save()
        messages.success(request, "Listing has been closed.")
    else:
        messages.error(request, "You are not the owner of this listing.")
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def add_comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to add a comment.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        
        # Get content from POST data
        content = request.POST.get('content', '').strip()
        
        # Validate content
        if not content:
            messages.error(request, "Comment cannot be empty.")
        else:
            # Create the comment
            Comment.objects.create(
                author=request.user,
                auction=listing,
                content=content
            )
            messages.success(request, "Your comment has been added successfully.")
        
        # Redirect back to the listing page
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    # If the request method is not POST, redirect to the listing page
    return HttpResponseRedirect('listing', listing_id=listing_id)

def rem_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user.is_authenticated:
        request.user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def add_to_watchlist(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(f'/listings/{listing_id}')

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user_watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        'user_watchlist': user_watchlist
    })

def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    comments = listing.comments.all()
    already_watching = request.user.is_authenticated and listing in request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        'listing': listing,
        'user': request.user,
        'already_watching': already_watching,
        'comments': comments
    })

def create_listing(request):
    if request.method == "POST":
        # Ensure starting_bid is a valid number
        try:
            starting_bid = float(request.POST["starting_bid"])
        except ValueError:
            return render(request, "auctions/create_listing.html", {
                "message": "Starting bid must be a valid number."
            })

        # Get the 'is_active' value from the checkbox, default to False if unchecked
        is_active = 'is_active' in request.POST  # True if checked, False otherwise

        # Validate required fields
        if not request.POST.get("title") or not request.POST.get("description"):
            return render(request, "auctions/create_listing.html", {
                "message": "Title and description are required fields."
            })

        # Create the new AuctionListing instance
        new_listing = AuctionListing(
            title=request.POST["title"],
            description=request.POST["description"],
            owner=request.user,
            starting_bid=starting_bid,
            current_price=starting_bid,
            image_url=request.POST.get("image_url", ""),  # Handle optional image_url
            is_active=is_active
        )
        new_listing.save()

        # Process and associate categories
        categories = request.POST.getlist('categories')  # Retrieves the list of selected categories
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            new_listing.categories.add(category)

        return HttpResponseRedirect(f'/listings/{new_listing.id}')

    # Render the form for GET requests
    return render(request, "auctions/create_listing.html", {
        'user': request.user,
        'categories': Category.objects.all()  # Pass categories to populate the form
    })


def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html",{
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
