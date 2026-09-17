import { TopNav } from "./components/TopNav";
import { Hero } from "./components/Hero";
import { TableOfContents } from "./components/TableOfContents";
import { Footer } from "./components/Footer";

import { SectionFloor } from "./sections/SectionFloor";
import { SectionContentMeaning } from "./sections/SectionContentMeaning";
import { SectionReceiver } from "./sections/SectionReceiver";
import { SectionTable } from "./sections/SectionTable";
import { SectionCatalysis } from "./sections/SectionCatalysis";
import { SectionCoherence } from "./sections/SectionCoherence";
import { SectionClosure } from "./sections/SectionClosure";
import { SectionRouteAudit } from "./sections/SectionRouteAudit";
import { SectionArchitecture } from "./sections/SectionArchitecture";
import { SectionDeployment } from "./sections/SectionDeployment";
import { SectionValidation } from "./sections/SectionValidation";

function App() {
  return (
    <div id="top">
      <TopNav />
      <Hero />
      <TableOfContents />
      <SectionFloor />
      <SectionContentMeaning />
      <SectionReceiver />
      <SectionTable />
      <SectionCatalysis />
      <SectionCoherence />
      <SectionClosure />
      <SectionRouteAudit />
      <SectionArchitecture />
      <SectionDeployment />
      <SectionValidation />
      <Footer />
    </div>
  );
}

export default App;
