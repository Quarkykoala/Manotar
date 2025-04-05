const { i18n } = require('./next-i18next.config')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  i18n,
  images: {
    domains: ['localhost'],
  },
  webpack(config) {
    // Enable code splitting
    config.optimization.splitChunks.chunks = 'all';
    return config;
  },
}

module.exports = nextConfig 