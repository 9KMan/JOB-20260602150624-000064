import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format, isValid } from 'date-fns';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return '';
  const d = typeof date === 'string' ? new Date(date) : date;
  if (!isValid(d)) return '';
  return format(d, 'MMM d, yyyy');
}

export function formatDateTime(date: Date | string | null | undefined): string {
  if (!date) return '';
  const d = typeof date === 'string' ? new Date(date) : date;
  if (!isValid(d)) return '';
  return format(d, 'MMM d, yyyy h:mm a');
}

export function formatRelativeTime(
  date: Date | string | null | undefined
): string {
  if (!date) return '';
  const d = typeof date === 'string' ? new Date(date) : date;
  if (!isValid(d)) return '';
  return formatDistanceToNow(d, { addSuffix: true });
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length).trim() + '...';
}

export function getInitials(name: string | null | undefined): string {
  if (!name) return '';
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

export function debounce<T extends (...args: Parameters<T>) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function sortByKey<T>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
}

export function groupBy<T, K extends keyof T>(
  array: T[],
  key: K
): Record<string, T[]> {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
}