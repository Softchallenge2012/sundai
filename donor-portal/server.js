const path = require('path');
const express = require('express');
const Stripe = require('stripe');
const nodemailer = require('nodemailer');
const dotenv = require('dotenv');

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

const app = express();
const port = Number(process.env.PORT || 4242);
const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
const publicBaseUrl = process.env.PUBLIC_BASE_URL || `http://localhost:${port}`;
const stripe = stripeSecretKey ? new Stripe(stripeSecretKey) : null;

app.get('/api/health', (_req, res) => {
  res.json({
    ok: true,
    stripeConfigured: Boolean(stripe),
    emailConfigured: Boolean(process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS),
  });
});

app.post('/api/create-checkout-session', express.json(), async (req, res) => {
  const { amount, donorName, donorEmail, frequency = 'once' } = req.body || {};
  const donationAmount = Number(amount || 0);

  if (!donorName || !donorEmail || donationAmount < 5) {
    return res.status(400).json({
      error: 'A valid donor name, email, and donation amount of at least $5 are required.',
    });
  }

  if (!stripe) {
    return res.status(501).json({
      error: 'Stripe is not configured. Set STRIPE_SECRET_KEY in .env.local to enable live checkout.',
    });
  }

  const isMonthly = frequency === 'monthly';
  const session = await stripe.checkout.sessions.create({
    mode: isMonthly ? 'subscription' : 'payment',
    success_url: `${publicBaseUrl}/?donation=success`,
    cancel_url: `${publicBaseUrl}/?donation=cancelled`,
    customer_email: donorEmail,
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: 'usd',
          unit_amount: Math.round(donationAmount * 100),
          product_data: {
            name: isMonthly ? 'Monthly donor support' : 'One-time donation',
            description: `${donorName} — ${isMonthly ? 'Monthly' : 'One-time'} gift`,
          },
          recurring: isMonthly ? { interval: 'month' } : undefined,
        },
      },
    ],
    metadata: {
      donorName,
      donorEmail,
      frequency,
      donationAmount: String(donationAmount),
    },
  });

  return res.json({
    ok: true,
    url: session.url,
    sessionId: session.id,
    mode: isMonthly ? 'subscription' : 'payment',
  });
});

app.post('/api/webhooks/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  if (!webhookSecret || !stripe) {
    return res.status(501).json({
      error: 'Stripe webhook secret is not configured. Set STRIPE_WEBHOOK_SECRET to enable automated email receipts.',
    });
  }

  const sig = req.headers['stripe-signature'];

  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (error) {
    console.error('Webhook signature verification failed:', error.message);
    return res.status(400).send(`Webhook Error: ${error.message}`);
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const donorName = session.metadata?.donorName || 'Supporter';
    const donorEmail = session.customer_details?.email || session.metadata?.donorEmail || session.customer_email;
    const amount = Number((session.amount_total || 0) / 100);
    const frequency = session.metadata?.frequency || 'once';

    if (donorEmail) {
      await sendDonationEmail({ donorName, donorEmail, amount, frequency });
    }
  }

  return res.status(200).json({ received: true });
});

app.post('/api/mock-donation-success', express.json(), async (req, res) => {
  const { donorName, donorEmail, amount, frequency = 'once' } = req.body || {};

  if (!donorName || !donorEmail || Number(amount || 0) < 5) {
    return res.status(400).json({ error: 'Valid donor name, email, and amount are required.' });
  }

  await sendDonationEmail({ donorName, donorEmail, amount: Number(amount), frequency });

  return res.json({ ok: true, note: 'Mock donation success processed; receipt/gratitude email triggered.' });
});

app.use(express.json());
app.use(express.static(__dirname));

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

async function sendDonationEmail({ donorName, donorEmail, amount, frequency }) {
  const smtpHost = process.env.SMTP_HOST;
  const smtpUser = process.env.SMTP_USER;
  const smtpPass = process.env.SMTP_PASS;

  if (!smtpHost || !smtpUser || !smtpPass) {
    console.log(`[email dry-run] Receipt sent to ${donorEmail} for ${donorName}: ${frequency === 'monthly' ? 'monthly' : 'one-time'} gift of $${amount}.`);
    return {
      ok: true,
      mode: 'dry-run',
      message: 'SMTP credentials missing; falling back to a local dry-run receipt log.',
    };
  }

  const transporter = nodemailer.createTransport({
    host: smtpHost,
    port: Number(process.env.SMTP_PORT || 587),
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: smtpUser,
      pass: smtpPass,
    },
  });

  const frequencyLabel = frequency === 'monthly' ? 'monthly' : 'one-time';
  const emailSubject = frequency === 'monthly'
    ? 'Thank you for your monthly support'
    : 'Thank you for your generous donation';

  const info = await transporter.sendMail({
    from: process.env.EMAIL_FROM || 'hello@communitygiving.org',
    to: donorEmail,
    subject: emailSubject,
    text: `Hi ${donorName},\n\nThank you for your ${frequencyLabel} gift of $${amount}. Your support helps us expand access to food, safety, and opportunity in our community.\n\nThis email serves as your receipt. We will send a summary of the impact of your support in the coming month.\n\nWith gratitude,\nNeighborhood Grant Partners`,
    html: `
      <div style="font-family: Arial, sans-serif; color: #1f2a22; line-height: 1.6;">
        <h2 style="color: #1d6c4d;">Thank you, ${donorName}</h2>
        <p>Thank you for your ${frequencyLabel} gift of <strong>$${amount}</strong>.</p>
        <p>Your support helps us expand access to food, safety, and opportunity in our community.</p>
        <p><strong>This email serves as your receipt.</strong> We are grateful for your generosity and the trust you place in us.</p>
        <p>With gratitude,<br />Neighborhood Grant Partners</p>
      </div>
    `,
  });

  console.log(`Receipt email sent to ${donorEmail}: ${info.messageId}`);
  return { ok: true, mode: 'smtp', messageId: info.messageId };
}

app.listen(port, () => {
  console.log(`Donor portal server is running at http://localhost:${port}`);
});
