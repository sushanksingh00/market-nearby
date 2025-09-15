import { Button } from "@/components/ui/button";
import { MapPin, Search, Store } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center bg-gradient-hero text-primary-foreground overflow-hidden">
      <div className="absolute inset-0 bg-black/10"></div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-white/20 rounded-full shadow-glow">
              <Store className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Shop Local
            <span className="block text-primary-glow">Stay Connected</span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-2xl mx-auto">
            Discover fresh products from shopkeepers in your neighborhood. 
            Support local businesses while shopping conveniently.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Button 
              size="lg" 
              variant="secondary"
              className="bg-white/20 border-white/30 text-white hover:bg-white/30 backdrop-blur-sm"
            >
              <MapPin className="w-5 h-5 mr-2" />
              Find Shops Near Me
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              className="border-white/30 text-white hover:bg-white/10 backdrop-blur-sm"
            >
              <Search className="w-5 h-5 mr-2" />
              Browse Products
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="text-center p-6 bg-white/10 rounded-lg backdrop-blur-sm">
              <div className="text-3xl font-bold mb-2">500+</div>
              <div className="text-white/80">Local Shops</div>
            </div>
            <div className="text-center p-6 bg-white/10 rounded-lg backdrop-blur-sm">
              <div className="text-3xl font-bold mb-2">10K+</div>
              <div className="text-white/80">Products</div>
            </div>
            <div className="text-center p-6 bg-white/10 rounded-lg backdrop-blur-sm">
              <div className="text-3xl font-bold mb-2">5KM</div>
              <div className="text-white/80">Max Radius</div>
            </div>
          </div>
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent"></div>
    </section>
  );
};

export default Hero;