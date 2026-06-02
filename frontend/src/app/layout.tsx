import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata = {
  title: {
    default: 'Premium Services Directory - Find Top-Rated Service Providers',
    template: '%s | Premium Services',
  },
  description:
    'Connect with the best service providers in your area. Browse thousands of verified professionals for home services, professional services, events, wellness, and more.',
  keywords: [
    'services',
    'directory',
    'professional services',
    'home services',
    'local services',
    'service providers',
  ],
  authors: [{ name: 'PremiumServices' }],
  creator: 'PremiumServices',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://premiumservices.com',
    siteName: 'PremiumServices',
    title: 'Premium Services Directory',
    description: 'Find top-rated service providers in your area',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Premium Services Directory',
    description: 'Find top-rated service providers in your area',
    creator: '@premiumservices',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      </head>
      <body className={inter.variable}>
        {children}
      </body>
    </html>
  );
}