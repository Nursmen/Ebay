from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import User, Listing


def index(request):
    listings = Listing.objects.all()
    # print url of first listing
    print(listings[0].image)

    return render(request, "auctions/index.html", {
        "listings": listings,
        'masage': 'Active Listings'
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

# function for create new listing
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        image = request.POST["image"]
        seller = request.user
        is_active = request.POST["is_active"]
        category = request.POST["category"]

        new_listing = Listing(title=title, description=description, price=price, image=image, seller=seller,
                              is_active=is_active, category=category)
        new_listing.save()
        return redirect('index')
    else:
        return render(request, "auctions/create.html")

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.session.get('message'):
        message = request.session.get('message')
        del request.session['message']

        return render(request, "auctions/listing.html", {
            "listing": listing,
            'user':request.user,
            'message': message
        })
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        'user':request.user
    })

# add listing to watchlist
def watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    user.watchlist.add(listing)
    
    return redirect('listing', listing_id=listing.id)


def deletefromwatchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    user.watchlist.remove(listing)

    return redirect('listing', listing_id=listing.id)

def mywatchlist(request):
    user = request.user
    listings = user.watchlist.all()
    return render(request, 'auctions/index.html', {
        'listings': listings,
        'masage': 'My Watchlist'
    })


def close(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.is_active = False
    listing.save()
    return redirect('index')

def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if float(request.POST['bid']) > float(listing.price):
        listing.price = request.POST['bid']
        listing.winner = request.user
        listing.save()
        return redirect('listing', listing_id=listing.id)
    else:
        request.session['message'] = 'Bid must be higher than current price'
        return redirect('listing', listing_id=listing.id)