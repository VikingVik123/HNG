# Invoice App - React Version

This is a React version of the invoice management application, converted from Vue 3.

## Features

- **Create Invoices**: Create new invoices with client details, items, and terms
- **Edit Invoices**: Modify existing invoices
- **Delete Invoices**: Remove invoices with confirmation
- **Mark as Paid**: Update invoice status to paid
- **Filter by Status**: Filter invoices by All, Draft, Pending, or Paid status
- **Dark/Light Mode**: Toggle between dark and light themes
- **LocalStorage**: Persist invoices to browser storage
- **Responsive Design**: Works on desktop and tablet

## Project Structure

```
src/
├── components/
│   ├── SideBar.jsx          # App sidebar with logo and theme toggle
│   ├── HeadComp.jsx         # Page header component
│   ├── FilterBar.jsx        # Filter dropdown component
│   ├── InvBox.jsx           # Invoice card component
│   ├── NewInvoice.jsx       # New invoice button
│   └── EmptyState.jsx       # Empty state component
├── pages/
│   ├── LandingPage.jsx      # Main invoice list page
│   ├── NewInvoicePage.jsx   # Create/edit invoice form
│   └── InvoiceDetailPage.jsx # Invoice detail view
├── context/
│   └── ThemeContext.jsx     # Theme provider and hook
├── router/
│   └── index.jsx            # Router configuration
├── App.jsx                  # Main app component
├── main.jsx                 # Entry point
└── style.css                # Global styles
```

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Technologies Used

- **React 18.2.0** - UI framework
- **React Router 6.20.1** - Client-side routing
- **Vite** - Build tool and dev server
- **CSS** - Styling with CSS custom properties for theming

## Theme System

The application uses CSS custom properties for theming. Colors are defined in `src/style.css`:

- Light mode: `#ffffff` background, `#0d1b2a` text
- Dark mode: `#1a1a2e` background, `#e8e8e8` text

## LocalStorage Structure

Invoices are stored as JSON in localStorage:

```javascript
{
  id: "INV-1234567890",
  billFrom: {
    streetAddress: "123 Main St",
    city: "New York",
    postCode: "10001",
    country: "USA"
  },
  billTo: {
    clientName: "John Doe",
    clientEmail: "john@example.com",
    streetAddress: "456 Oak Ave",
    city: "Los Angeles",
    postCode: "90001",
    country: "USA"
  },
  invoiceDate: "2024-04-23",
  paymentTerms: "Net 30 Days",
  projectDescription: "Project details...",
  items: [
    {
      name: "Item 1",
      quantity: 2,
      price: 100,
      total: 200
    }
  ],
  status: "draft" // or "pending", "paid"
}
```

## Routes

- `/` - Landing page (invoice list)
- `/new-invoice` - Create new invoice / Edit invoice (query param: `?id=invoiceId`)
- `/invoice/:id` - Invoice detail page

## Styling

Each component has its own CSS file for scoped styling. Global styles and theme variables are in `src/style.css`.

### Color Variables

- `--bg-primary` - Primary background
- `--bg-secondary` - Secondary background
- `--text-primary` - Primary text color
- `--text-secondary` - Secondary text color
- `--border-color` - Border color
- `--card-bg` - Card background
- `--input-bg` - Input background

## Form Validation

The NewInvoicePage includes comprehensive form validation for:
- Required fields (Bill From/To, Client info, Items)
- Email format validation
- Quantity and price validation

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

- Mobile responsive improvements
- PDF export functionality
- Email invoice functionality
- Payment status tracking
- User authentication
- Cloud storage integration
