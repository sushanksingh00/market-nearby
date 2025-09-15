import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, Search } from "lucide-react";

const LocationSelector = () => {
  const [location, setLocation] = useState("");
  const [radius, setRadius] = useState("5");

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-medium">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center gap-2 text-primary">
          <MapPin className="w-6 h-6" />
          Find Shops Near You
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative">
          <Input
            placeholder="Enter your location or address"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="pl-10"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        </div>
        
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Search Radius</label>
          <Select value={radius} onValueChange={setRadius}>
            <SelectTrigger>
              <SelectValue placeholder="Select radius" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1 KM</SelectItem>
              <SelectItem value="2">2 KM</SelectItem>
              <SelectItem value="5">5 KM</SelectItem>
              <SelectItem value="10">10 KM</SelectItem>
              <SelectItem value="15">15 KM</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button className="w-full" size="lg">
          <Search className="w-4 h-4 mr-2" />
          Search Shops
        </Button>

        <div className="flex justify-center">
          <Button variant="ghost" size="sm" className="text-primary">
            <MapPin className="w-4 h-4 mr-2" />
            Use Current Location
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default LocationSelector;