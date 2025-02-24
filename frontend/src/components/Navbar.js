import React from 'react';
import { Button } from './ui/button';

const Navigation = () => {
  return (
    <nav className="fixed w-full z-50 bg-white/90 backdrop-blur-sm shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <a href="/" className="text-2xl font-bold text-film-900">
            Filmila
          </a>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="/browse" className="nav-link">
              Browse Films
            </a>
            <a href="/about" className="nav-link">
              About
            </a>
            <a href="/contact" className="nav-link">
              Contact
            </a>
          </div>

          <div className="flex items-center space-x-4">
            <Button variant="outline" className="text-film-900 border-film-900">
              Sign In
            </Button>
            <Button>
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
