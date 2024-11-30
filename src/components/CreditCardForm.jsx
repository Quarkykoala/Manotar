import React, { useState } from 'react';
import Cards from 'react-credit-cards-2';
import 'react-credit-cards-2/dist/es/styles-compiled.css';

const CreditCardForm = () => {
  const [state, setState] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: '',
    focus: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setState(prev => ({ ...prev, [name]: value }));
  };

  const handleInputFocus = (e) => {
    setState(prev => ({ ...prev, focus: e.target.name }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle payment processing here
    console.log('Form submitted:', state);
  };

  return (
    <div className="card-form-container">
      <Cards
        number={state.number}
        expiry={state.expiry}
        cvc={state.cvc}
        name={state.name}
        focused={state.focus}
      />
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            name="number"
            placeholder="Card Number"
            value={state.number}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            maxLength="16"
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            name="name"
            placeholder="Cardholder Name"
            value={state.name}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <input
              type="text"
              name="expiry"
              placeholder="MM/YY"
              value={state.expiry}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              maxLength="4"
              required
            />
          </div>
          <div className="form-group">
            <input
              type="text"
              name="cvc"
              placeholder="CVC"
              value={state.cvc}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              maxLength="3"
              required
            />
          </div>
        </div>
        <button type="submit">Submit Payment</button>
      </form>
    </div>
  );
};

export default CreditCardForm;
