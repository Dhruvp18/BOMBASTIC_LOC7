import React from 'react';
import useInvoicesByCompany from '../hooks/useInvoicesByCompany';

const CompanyInvoiceList = ({ companyName }) => {
    // Call the custom hook with the company name
    const { invoices, loading, error } = useInvoicesByCompany(companyName);
    console.log(invoices);
    
    // Render loading state
    if (loading) {
        return <p>Loading invoices...</p>;
    }

    // Render error state
    if (error) {
        return <p>Error: {error}</p>;
    }

    // Render the list of invoices
    return (
        <div>
            <h2>Invoices for {companyName}</h2>
            {invoices.length === 0 ? (
                <p>No invoices found for this company.</p>
            ) : (
                <ul>
                    {invoices.map((invoice) => (
                        <li key={invoice._id}>
                            <strong>Invoice Number:</strong> {invoice.bill.invoice_number},{' '}
                            <strong>Total Amount:</strong> {invoice.bill.totalAmount}{' '}
                            {invoice.bill.currency}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default CompanyInvoiceList;