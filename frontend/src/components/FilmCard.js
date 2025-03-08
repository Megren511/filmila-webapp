import React from 'react';
import { Button } from './ui/button';

const FilmCard = ({ title, director, duration, genre, imageUrl, price }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden transition-transform duration-300 hover:-translate-y-1">
      <div className="relative h-48">
        <img
          src={imageUrl}
          alt={title}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-6">
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 mb-1">Director: {director}</p>
        <div className="flex justify-between items-center mb-4">
          <span className="text-gray-500">{duration}</span>
          <span className="text-gray-500">{genre}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-film-600">${price}</span>
          <Button variant="primary" className="text-sm">
            Watch Now
          </Button>
        </div>
      </div>
    </div>
  );
};

export default FilmCard;
