import React from 'react';

const Button = ({ children, className = '', variant = 'primary', ...props }) => {
  const baseStyles = 'px-6 py-3 rounded-lg font-medium transition-all duration-200';
  
  const variants = {
    primary: 'bg-film-600 text-white hover:bg-film-700 shadow-lg hover:shadow-xl',
    outline: 'bg-transparent hover:bg-opacity-10',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export { Button };
