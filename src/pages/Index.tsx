import Header from "@/components/Header";
import Hero from "@/components/Hero";
import LocationSelector from "@/components/LocationSelector";
import ShopCard from "@/components/ShopCard";
import ProductCard from "@/components/ProductCard";
import vegetableShopImage from "@/assets/vegetable-shop.jpg";
import tomatoesImage from "@/assets/tomatoes.jpg";
import breadImage from "@/assets/bread.jpg";
import dairyImage from "@/assets/dairy.jpg";

const Index = () => {
  // Mock data for demonstration
  const mockShops = [
    {
      name: "Green Valley Vegetables",
      address: "123 Market Street, Downtown",
      distance: "0.8 km",
      rating: 4.5,
      isOpen: true,
      categories: ["Vegetables", "Fruits", "Organic"],
      phone: "+91 98765 43210",
      image: vegetableShopImage,
    },
    {
      name: "Fresh Daily Market",
      address: "456 Garden Road, Central",
      distance: "1.2 km", 
      rating: 4.3,
      isOpen: true,
      categories: ["Groceries", "Dairy", "Snacks"],
      phone: "+91 98765 43211",
      image: vegetableShopImage,
    },
    {
      name: "Golden Bakery",
      address: "789 Bread Lane, Old Town",
      distance: "1.8 km",
      rating: 4.7,
      isOpen: false,
      categories: ["Bakery", "Pastries", "Coffee"],
      phone: "+91 98765 43212",
      image: vegetableShopImage,
    }
  ];

  const mockProducts = [
    {
      name: "Fresh Organic Tomatoes",
      price: 45,
      originalPrice: 60,
      image: tomatoesImage,
      shopName: "Green Valley Vegetables",
      category: "Vegetables",
      inStock: true,
      rating: 4.5,
      discount: 25,
    },
    {
      name: "Artisan Sourdough Bread",
      price: 120,
      image: breadImage,
      shopName: "Golden Bakery",
      category: "Bakery",
      inStock: true,
      rating: 4.8,
    },
    {
      name: "Fresh Dairy Milk",
      price: 55,
      image: dairyImage,
      shopName: "Fresh Daily Market",
      category: "Dairy",
      inStock: false,
      rating: 4.2,
    },
    {
      name: "Organic Baby Spinach",
      price: 35,
      originalPrice: 45,
      image: tomatoesImage,
      shopName: "Green Valley Vegetables",
      category: "Vegetables",
      inStock: true,
      rating: 4.6,
      discount: 22,
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main>
        {/* Hero Section */}
        <Hero />
        
        {/* Location Selector */}
        <section className="py-16 px-4">
          <div className="container mx-auto">
            <LocationSelector />
          </div>
        </section>

        {/* Featured Shops */}
        <section className="py-16 px-4 bg-secondary/30">
          <div className="container mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Shops Near You
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Discover local businesses in your area offering fresh products and daily essentials
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockShops.map((shop, index) => (
                <ShopCard key={index} {...shop} />
              ))}
            </div>
          </div>
        </section>

        {/* Featured Products */}
        <section className="py-16 px-4">
          <div className="container mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Fresh Products Today
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Browse today's fresh arrivals from local shopkeepers in your area
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {mockProducts.map((product, index) => (
                <ProductCard key={index} {...product} />
              ))}
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-16 px-4 bg-gradient-hero text-primary-foreground">
          <div className="container mx-auto text-center">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Start Shopping?
            </h2>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              Join thousands of customers supporting local businesses in their community
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-3 bg-white/20 border border-white/30 text-white rounded-lg hover:bg-white/30 transition-colors backdrop-blur-sm">
                Sign Up as Customer
              </button>
              <button className="px-8 py-3 border border-white/30 text-white rounded-lg hover:bg-white/10 transition-colors backdrop-blur-sm">
                Become a Shopkeeper
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-foreground text-background py-12 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4">LocalShop</h3>
              <p className="text-background/80">
                Connecting communities through local commerce
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Customers</h4>
              <ul className="space-y-2 text-background/80">
                <li>Find Shops</li>
                <li>Browse Products</li>
                <li>Track Orders</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">For Shopkeepers</h4>
              <ul className="space-y-2 text-background/80">
                <li>List Your Shop</li>
                <li>Manage Inventory</li>
                <li>View Analytics</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-background/80">
                <li>Help Center</li>
                <li>Contact Us</li>
                <li>Terms & Privacy</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-background/20 mt-8 pt-8 text-center text-background/60">
            <p>&copy; 2025 LocalShop. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
