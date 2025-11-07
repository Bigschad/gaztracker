import { Link } from 'react-router-dom';
import { Button } from '../components/common';
import { Home } from 'lucide-react';

const NotFoundPage = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary">404</h1>
        <p className="mt-4 text-2xl font-semibold">Page non trouvée</p>
        <p className="mt-2 text-muted-foreground">
          La page que vous recherchez n'existe pas.
        </p>
        <Link to="/dashboard" className="mt-6 inline-block">
          <Button>
            <Home className="mr-2 h-4 w-4" />
            Retour à l'accueil
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
