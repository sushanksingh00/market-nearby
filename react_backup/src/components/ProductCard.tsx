import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShoppingCart, Heart, Star } from "lucide-react";
import { useState } from "react";

interface ProductCardProps {
  name: string;
  price: number;
  originalPrice?: number;
  image: string;
  shopName: string;
  category: string;
  inStock: boolean;
  rating: number;
  discount?: number;
}

const ProductCard = ({ 
  name, 
  price, 
  originalPrice, 
  image, 
  shopName, 
  category, 
  inStock, 
  rating,
  discount 
}: ProductCardProps) => {
  const [isWishlisted, setIsWishlisted] = useState(false);

  return (
    <Card className="overflow-hidden hover:shadow-medium transition-all duration-300 hover:-translate-y-1 animate-scale-in">
      <div className="relative h-48 bg-gradient-card overflow-hidden group">
        <img 
          src={image} 
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {discount && (
          <div className="absolute top-3 left-3">
            <Badge className="bg-destructive text-destructive-foreground">
              -{discount}%
            </Badge>
          </div>
        )}
        <button
          onClick={() => setIsWishlisted(!isWishlisted)}
          className="absolute top-3 right-3 p-2 bg-white/80 rounded-full hover:bg-white transition-colors"
        >
          <Heart 
            className={`w-4 h-4 ${isWishlisted ? 'fill-destructive text-destructive' : 'text-muted-foreground'}`} 
          />
        </button>
        {!inStock && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <Badge variant="secondary" className="bg-white/90">
              Out of Stock
            </Badge>
          </div>
        )}
      </div>
      
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
          <Badge variant="outline" className="text-xs">
            {category}
          </Badge>
          <span>•</span>
          <span>{shopName}</span>
        </div>
        <CardTitle className="text-lg line-clamp-2">{name}</CardTitle>
        <div className="flex items-center gap-1">
          <Star className="w-4 h-4 fill-warning text-warning" />
          <span className="text-sm text-muted-foreground">{rating}</span>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-bold text-primary">₹{price}</span>
          {originalPrice && (
            <span className="text-sm text-muted-foreground line-through">₹{originalPrice}</span>
          )}
        </div>
        
        <Button 
          className="w-full" 
          size="sm"
          disabled={!inStock}
        >
          <ShoppingCart className="w-4 h-4 mr-2" />
          {inStock ? 'Add to Cart' : 'Out of Stock'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default ProductCard;