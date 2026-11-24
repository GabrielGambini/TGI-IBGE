import About from "./components/About";
import Footer from "./components/Footer";
import Groups from "./components/Groups";
import Hero from "./components/Hero";
import Indicators from "./components/Indicators";
import Methodology from "./components/Methodology";
import Navbar from "./components/Navbar";
import PowerBI from "./components/PowerBI";
import Sources from "./components/Sources";

export default function App() {
  return (
    <>
      <Navbar />
      <main>
        <Hero /><About /><Indicators /><PowerBI /><Groups /><Methodology /><Sources />
      </main>
      <Footer />
    </>
  );
}
