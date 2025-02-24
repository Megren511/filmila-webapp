import Navigation from "../components/Navigation";
import FilmCard from "../components/FilmCard";
import { Button } from "../components/ui/button";

const mockFilms = [
  {
    title: "The Silent Echo",
    director: "Sarah Chen",
    duration: "15 min",
    genre: "Drama",
    imageUrl: "https://images.unsplash.com/photo-1536440136628-849c177e76a1",
    price: 2.99,
  },
  {
    title: "Urban Dreams",
    director: "Michael Torres",
    duration: "12 min",
    genre: "Contemporary",
    imageUrl: "https://images.unsplash.com/photo-1478720568477-152d9b164e26",
    price: 1.99,
  },
  {
    title: "Nature's Whisper",
    director: "Emma Wilson",
    duration: "18 min",
    genre: "Documentary",
    imageUrl: "https://images.unsplash.com/photo-1518134346374-184f9d21cea2",
    price: 3.99,
  },
];

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
            alt="Hero background"
            className="object-cover w-full h-full"
          />
          <div className="absolute inset-0 bg-black/50" />
        </div>
        
        <div className="container mx-auto px-4 relative z-10 text-center">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 animate-fade-up">
            Watch Independent Films
          </h1>
          <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-2xl mx-auto animate-fade-up" style={{ animationDelay: "0.2s" }}>
            Discover unique stories from talented filmmakers around the world.
          </p>
          <Button className="button-primary text-lg animate-fade-up" style={{ animationDelay: "0.4s" }}>
            Start Watching
          </Button>
        </div>
      </section>

      {/* Featured Films */}
      <section className="page-container py-20">
        <h2 className="text-3xl font-bold text-center mb-12">Featured Films</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {mockFilms.map((film, index) => (
            <FilmCard key={index} {...film} />
          ))}
        </div>
      </section>

      {/* Call to Action */}
      <section className="bg-film-900 text-white mt-20">
        <div className="container mx-auto px-4 text-center py-20">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Are you a filmmaker?
          </h2>
          <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
            Share your work with our growing community of film enthusiasts.
          </p>
          <Button variant="outline" className="border-2 border-white text-white hover:bg-white hover:text-film-900">
            Start Uploading
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Index;
