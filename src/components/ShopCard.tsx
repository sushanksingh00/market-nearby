import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Clock, Star, Phone } from "lucide-react";

interface ShopCardProps {
  name: string;
  address: string;
  distance: string;
  rating: number;
  isOpen: boolean;
  categories: string[];
  phone: string;
  image: string;
}

const ShopCard = ({ name, address, distance, rating, isOpen, categories, phone, image }: ShopCardProps) => {
  return (
    <Card className="overflow-hidden hover:shadow-medium transition-all duration-300 hover:-translate-y-1 animate-fade-in">
      <div className="relative h-48 bg-gradient-card overflow-hidden">
        <img 
          src={image} 
          alt={name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-4 right-4">
          <Badge variant={isOpen ? "default" : "secondary"} className="bg-gradient-primary border-0">
            <Clock className="w-3 h-3 mr-1" />
            {isOpen ? "Open" : "Closed"}
          </Badge>
        </div>
        <div className="absolute top-4 left-4">
          <Badge variant="secondary" className="bg-white/90 text-foreground">
            <MapPin className="w-3 h-3 mr-1" />
            {distance}
          </Badge>
        </div>
      </div>
      
      <CardHeader className="pb-2">
        <CardTitle className="text-xl text-foreground">{name}</CardTitle>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="w-4 h-4" />
          <span>{address}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center">
            <Star className="w-4 h-4 fill-warning text-warning" />
            <span className="ml-1 text-sm font-medium">{rating}</span>
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <Phone className="w-4 h-4 mr-1" />
            {phone}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="flex flex-wrap gap-2 mb-4">
          {categories.map((category) => (
            <Badge key={category} variant="outline" className="text-xs">
              {category}
            </Badge>
          ))}
        </div>
        
        <div className="flex gap-2">
          <Button className="flex-1" size="sm">
            View Products
          </Button>
          <Button variant="outline" size="sm">
            Call Shop
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ShopCard;