const amountButtons = document.querySelectorAll('.amount-btn');
const customAmountInput = document.getElementById('custom-amount');
const form = document.getElementById('donation-form');
const successMessage = document.getElementById('donation-success');

let selectedAmount = 50;

const syncSelection = (amount) => {
  selectedAmount = Number(amount);
  customAmountInput.value = selectedAmount;

  amountButtons.forEach((button) => {
    const isActive = Number(button.dataset.amount) === selectedAmount;
    button.classList.toggle('active', isActive);
  });
};

amountButtons.forEach((button) => {
  button.addEventListener('click', () => {
    syncSelection(button.dataset.amount);
  });
});

customAmountInput.addEventListener('input', () => {
  const value = Number(customAmountInput.value || 0);
  if (value > 0) {
    syncSelection(value);
  }
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const donorName = document.getElementById('donor-name').value.trim();
  const donorEmail = document.getElementById('donor-email').value.trim();
  const frequency = formData.get('frequency');

  if (!donorName || !donorEmail) {
    return;
  }

  const donationSummary = {
    amount: selectedAmount,
    frequency,
    donorName,
    donorEmail,
    createdAt: new Date().toISOString(),
  };

  localStorage.setItem('donationSummary', JSON.stringify(donationSummary));
  successMessage.classList.remove('hidden');
  successMessage.textContent = `Thanks, ${donorName}. We’re preparing a secure build-fund check-out for your ${frequency === 'monthly' ? 'monthly' : 'one-time'} support of $${selectedAmount}.`;

  try {
    const response = await fetch('/api/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: selectedAmount,
        donorName,
        donorEmail,
        frequency,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Unable to start secure checkout.');
    }

    if (data.url) {
      window.location.href = data.url;
      return;
    }

    successMessage.textContent = 'The build-fund checkout is ready, but no redirect URL was returned.';
  } catch (error) {
    successMessage.textContent = error.message || 'Something went wrong while starting secure checkout.';
    console.error(error);
  }
});

syncSelection(50);
