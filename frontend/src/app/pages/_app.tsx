import 'bootstrap/dist/css/bootstrap.min.css'; // Importing Bootstrap CSS
import { AppProps } from 'next/app';

// This is the custom App component that wraps every page in your app
function MyApp({ Component, pageProps }: AppProps) {
    return <Component {...pageProps} />;
}

export default MyApp;
