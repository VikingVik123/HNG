import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from '../pages/LandingPage';
import NewInvoicePage from '../pages/NewInvoicePage';
import InvoiceDetailPage from '../pages/InvoiceDetailPage';

export const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/new-invoice" element={<NewInvoicePage />} />
        <Route path="/invoice/:id" element={<InvoiceDetailPage />} />
      </Routes>
    </Router>
  );
};
