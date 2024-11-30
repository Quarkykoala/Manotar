import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const locations = [
  "All Locations",
  "Headquarters",
  "Remote",
  "Branch Office 1",
  "Branch Office 2",
  "Regional Hub"
];

interface LocationFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export const LocationFilter = ({ value, onChange }: LocationFilterProps) => (
  <Select value={value} onValueChange={onChange}>
    <SelectTrigger className="w-[180px]">
      <SelectValue placeholder="Select Location" />
    </SelectTrigger>
    <SelectContent>
      {locations.map((location) => (
        <SelectItem key={location} value={location.toLowerCase()}>
          {location}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
); 