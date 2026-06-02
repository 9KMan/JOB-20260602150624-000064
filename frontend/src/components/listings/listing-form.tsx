'use client';

import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Upload, X, Plus, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Switch } from '@/components/ui/switch';
import { listingSchema, type CreateListingInput } from '@/lib/validations/listing';
import { cn } from '@/lib/utils';
import Image from 'next/image';

interface ListingFormProps {
  initialData?: Partial<CreateListingInput>;
  onSubmit: (data: CreateListingInput) => Promise<void>;
  isLoading?: boolean;
}

const categoryOptions = [
  { value: 'home-services', label: 'Home Services' },
  { value: 'professional', label: 'Professional Services' },
  { value: 'events', label: 'Events & Entertainment' },
  { value: 'wellness', label: 'Health & Wellness' },
  { value: 'technology', label: 'Technology & IT' },
  { value: 'education', label: 'Education & Training' },
];

const priceTypeOptions = [
  { value: 'fixed', label: 'Fixed Price' },
  { value: 'hourly', label: 'Hourly Rate' },
  { value: 'starting_at', label: 'Starting At' },
  { value: 'quote', label: 'Request Quote' },
];

export function ListingForm({
  initialData,
  onSubmit,
  isLoading = false,
}: ListingFormProps) {
  const [images, setImages] = useState<Array<{ url: string; file?: File }>>(
    initialData?.images?.map((img) => ({ url: img.url })) || []
  );

  const form = useForm<CreateListingInput>({
    resolver: zodResolver(listingSchema),
    defaultValues: {
      title: initialData?.title || '',
      shortDescription: initialData?.shortDescription || '',
      description: initialData?.description || '',
      price: initialData?.price || 0,
      priceType: initialData?.priceType || 'fixed',
      categoryId: initialData?.categoryId || '',
      featured: initialData?.featured || false,
      premium: initialData?.premium || false,
      status: initialData?.status || 'draft',
      images: initialData?.images || [],
    },
  });

  const handleImageUpload = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (!files) return;

      const newImages = Array.from(files).map((file) => ({
        url: URL.createObjectURL(file),
        file,
      }));

      setImages((prev) => [...prev, ...newImages].slice(0, 10));
    },
    []
  );

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (data: CreateListingInput) => {
    const finalData: CreateListingInput = {
      ...data,
      images: images.map((img, i) => ({
        url: img.url,
        alt: `${data.title} image ${i + 1}`,
      })),
    };
    await onSubmit(finalData);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-8">
        <div className="grid gap-6 md:grid-cols-2">
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Title</FormLabel>
                <FormControl>
                  <Input placeholder="Professional home cleaning service" {...field} />
                </FormControl>
                <FormDescription>
                  A clear, descriptive title for your service
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="categoryId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Category</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a category" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {categoryOptions.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="priceType"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price Type</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select price type" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {priceTypeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          {form.watch('priceType') !== 'quote' && (
            <FormField
              control={form.control}
              name="price"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    {form.watch('priceType') === 'starting_at'
                      ? 'Starting Price'
                      : form.watch('priceType') === 'hourly'
                      ? 'Hourly Rate'
                      : 'Price'}
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="0.00"
                      {...field}
                      onChange={(e) =>
                        field.onChange(parseFloat(e.target.value) || 0)
                      }
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
        </div>

        <FormField
          control={form.control}
          name="shortDescription"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Short Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="A brief overview of your service (20-300 characters)"
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                This appears on listing cards and search results
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Detailed description of your service, experience, and what clients can expect..."
                  className="min-h-[200px] resize-none"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Provide a comprehensive description to help clients understand your
                services
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="space-y-2">
          <Label>Images (up to 10)</Label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {images.map((image, index) => (
              <div
                key={index}
                className="relative aspect-square rounded-lg overflow-hidden border"
              >
                <Image
                  src={image.url}
                  alt={`Upload ${index + 1}`}
                  fill
                  className="object-cover"
                />
                <Button
                  type="button"
                  variant="destructive"
                  size="icon"
                  className="absolute top-1 right-1 h-6 w-6"
                  onClick={() => removeImage(index)}
                >
                  <X className="h-3 w-3" />
                </Button>
                {index === 0 && (
                  <span className="absolute bottom-1 left-1 bg-black/60 text-white text-xs px-1.5 py-0.5 rounded">
                    Cover
                  </span>
                )}
              </div>
            ))}

            {images.length < 10 && (
              <label className="flex aspect-square cursor-pointer items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25 hover:border-muted-foreground/50 transition-colors">
                <div className="flex flex-col items-center gap-1 text-muted-foreground">
                  <Upload className="h-6 w-6" />
                  <span className="text-xs">Upload</span>
                </div>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={handleImageUpload}
                />
              </label>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            First image will be used as the cover photo
          </p>
        </div>

        <div className="flex items-center gap-6">
          <FormField
            control={form.control}
            name="featured"
            render={({ field }) => (
              <FormItem className="flex items-center gap-2">
                <FormControl>
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="!mb-0">Featured Listing</FormLabel>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="premium"
            render={({ field }) => (
              <FormItem className="flex items-center gap-2">
                <FormControl>
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="!mb-0">Premium Listing</FormLabel>
              </FormItem>
            )}
          />
        </div>

        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => form.reset()}
            disabled={isLoading}
          >
            Reset
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {initialData?.title ? 'Update Listing' : 'Create Listing'}
          </Button>
        </div>
      </form>
    </Form>
  );
}

import { FormDescription } from '@/components/ui/form';