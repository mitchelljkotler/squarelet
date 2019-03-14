/// <reference types="stripe-v3" />

import {d, exists, on} from './util';
// import { StripeAPIError } from 'stripe/lib/Error';
// const Stripe = require('stripe') as StripeAPIError;
// // TODO: get Stripe import to work.
// const Stripe = window['Stripe'] as any;

/**
 * A Squarelet plan.
 */
interface Plan {
  pk: number;
  base_price: number;
  price_per_user: number;
  minimum_users: number;
}

// Style for the Stripe card element.
const STRIPE_STYLE = {
  base: {
    color: '#3F3F3F',
    fontSize: '18px',
    fontFamily: 'system-ui, sans-serif',
    fontSmoothing: 'antialiased',
    '::placeholder': {
      color: '#899194',
    },
  },
  invalid: {
    color: '#e5424d',
    ':focus': {
      color: '#303238',
    },
  },
};

/**
 * Set up and handle reactive views related to paid plans.
 */
export class PlansView {
  readonly stripePk = d('id_stripe_pk') as HTMLInputElement; // hidden Stripe key
  readonly planInput = d('id_plan') as HTMLInputElement;
  readonly ucofInput = d('id_use_card_on_file') as HTMLInputElement;
  readonly ccFieldset = d('_id-cardFieldset');

  readonly planInfoElem = d('_id-planInfo'); // Pane to show plan information
  readonly planProjection = d('_id-planProjection'); // Plan projection information
  readonly cardContainer = d('card-container'); // Credit card container.

  readonly receiptEmails = d('_id-receiptEmails') as HTMLTextAreaElement;
  readonly totalCost = d('_id-totalCost');
  readonly costBreakdown = d('_id-costBreakdown');

  readonly maxUsersElem = d('id_max_users') as HTMLInputElement | null;

  readonly planInfo: {[key: number]: Plan} = JSON.parse(this.planInfoElem.textContent);

  public maxUsers: number;

  constructor() {
    this.setupMaxUsersField();
    this.setupCardOnFileField();
    this.setupReceiptEmails();
    this.setupStripe();
    this.updateAll();
  }

  /**
   * Resize the receipt emails to match the text content.
   */
  receiptResize() {
    // Set a small initial height to derive the scroll height.
    this.receiptEmails.style.height = '5px';
    this.receiptEmails.style.height = this.receiptEmails.scrollHeight + 'px';
  }

  /**
   * Returns the currently selected plan information.
   */
  getPlan(): Plan {
    return this.planInfo[this.planInput.value];
  }

  /**
   * Update the total cost breakdown text.
   * TODO: figure out i18n for these strings
   */
  updateTotalCost() {
    const plan = this.getPlan();
    const cost = `${plan.base_price +
      (this.maxUsers - plan.minimum_users) * plan.price_per_user}`;
    const costFormatted = `$${cost}`;
    this.totalCost.textContent = costFormatted;

    let costBreakdownFormatted = `$${plan.base_price} (base price)`;
    if (this.maxUsers != 0) {
      if (this.maxUsers - plan.minimum_users == 0) {
        costBreakdownFormatted += ` with ${plan.minimum_users} user${
          plan.minimum_users != 1 ? 's' : ''
        } included`;
        if (plan.price_per_user != 0) {
          costBreakdownFormatted += ` ($${plan.price_per_user} per additional user)`;
        }
      } else {
        costBreakdownFormatted += ` with ${plan.minimum_users} user${
          plan.minimum_users != 1 ? 's' : ''
        } included and ${this.maxUsers - plan.minimum_users} extra users at $${
          plan.price_per_user
        } each`;
      }
    }
    this.costBreakdown.textContent = costBreakdownFormatted;
  }

  /**
   * Handle updates to the plan selection.
   */
  updatePlanInput() {
    const plan = this.getPlan();
    const isFreePlan = isFree(plan);

    this.updateTotalCost();

    // TODO: use util function for this display logic.
    if (isFreePlan) {
      if (this.ccFieldset != null) {
        this.ccFieldset.style.display = 'none';
      }
      if (this.planProjection != null) {
        this.planProjection.style.display = 'none';
      }
    } else {
      if (this.ccFieldset != null) {
        this.ccFieldset.style.display = '';
      }
      if (this.planProjection != null) {
        this.planProjection.style.display = '';
      }
    }
    this.updateAll(false);
  }

  /**
   * Handle changes to the max users element.
   */
  updateMaxUsers() {
    if (this.maxUsersElem == null) return;
    this.maxUsers = parseInt(this.maxUsersElem.value);
    const minUsers = this.getPlan().minimum_users;
    this.maxUsersElem.min = `${minUsers}`;
    if (this.maxUsers < minUsers) {
      this.maxUsersElem.value = `${minUsers}`;
      this.maxUsers = minUsers;
    }
  }

  /**
   * Handle changes to the saved credit card selection.
   */
  updateSavedCC() {
    if (this.ucofInput == null) {
      if (isFree(this.getPlan())) {
        if (this.cardContainer != null) {
          this.cardContainer.style.display = 'none';
        }
      } else {
        if (this.cardContainer != null) {
          this.cardContainer.style.display = '';
        }
      }
      return;
    }
    const ucofInput = document.querySelector(
      'input[name=use_card_on_file]:checked'
    ) as HTMLInputElement;
    if (ucofInput.value == 'True') {
      if (this.cardContainer != null) {
        // TODO: Use utility hide function
        this.cardContainer.style.display = 'none';
      }
    } else {
      if (this.cardContainer != null) {
        this.cardContainer.style.display = '';
      }
    }
  }

  /**
   * Updates the max users, saved credit card, and plan input selections simultaneously.
   * This method is used to safely ensure changes are recognized by all reactive
   * components.
   * @param updatePlanInput Whether to also update the plan input. This is set to false
   * when the plan input calls this method to avoid infinite loops.
   */
  updateAll(updatePlanInput = true) {
    this.updateMaxUsers();
    this.updateSavedCC();
    if (updatePlanInput) this.updatePlanInput();
  }

  /**
   * Set up event listeners and variables related to the max users setting.
   */
  setupMaxUsersField() {
    if (exists('id_max_users')) {
      // Handle reactive max user updates if field is defined.
      const maxUsersElem = this.maxUsersElem as HTMLInputElement;
      this.maxUsers = parseInt(maxUsersElem.value);
      on(maxUsersElem, 'input', () => {
        this.updateAll();
      });
    } else {
      this.maxUsers = 1;
    }
  }

  /**
   * Set up event listeners and variables related to the card on file field.
   */
  setupCardOnFileField() {
    if (exists('id_use_card_on_file')) {
      on(this.ucofInput, 'input', () => {
        this.updateAll();
      });
    }
  }

  /**
   * Set up event listeners and variables related to the receipt emails field.
   */
  setupReceiptEmails() {
    if (this.receiptEmails == null) return;
    // Make receipt emails field auto-resize.
    this.receiptEmails.rows = 2;
    on(this.receiptEmails, 'input', () => this.receiptResize());
    this.receiptResize();
  }

  /**
   * Set up event listeners and variables related to Stripe.
   */
  setupStripe() {
    if (exists('card-element')) {
      const stripe = Stripe(this.stripePk.value);
      const elements = stripe.elements();

      // Decorate card.
      const card = elements.create('card', {style: STRIPE_STYLE});
      card.mount('#card-element');
      ((card as unknown) as HTMLElement).addEventListener('change', event => {
        const changeEvent = event as {error?: {message: string}};
        // Show Stripe errors.
        const displayError = document.getElementById('card-errors');
        if (changeEvent.error) {
          displayError.textContent = changeEvent.error.message;
        } else {
          displayError.textContent = '';
        }
      });

      // We don't want the browser to fill this in with old values
      (document.getElementById('id_stripe_token') as HTMLInputElement).value = '';

      // only show payment fields if needed

      this.planInput.addEventListener('input', () => {
        this.updateAll();
      });

      // Create a token or display an error when the form is submitted.
      const form = document.getElementById('stripe-form');
      form.addEventListener('submit', event => {
        const ucofInput = document.querySelector(
          'input[name=use_card_on_file]:checked'
        ) as HTMLInputElement;

        const useCardOnFile = ucofInput != null && ucofInput.value == 'True';
        const plan = this.getPlan();

        const isFreePlan = isFree(plan);
        if (!useCardOnFile && !isFreePlan) {
          event.preventDefault();

          stripe.createToken(card).then(function(result) {
            if (result.error) {
              // Inform the customer that there was an error.
              const errorElement = document.getElementById('card-errors');
              errorElement.textContent = result.error.message;
            } else {
              // Send the token to your server.
              stripeTokenHandler(result.token);
            }
          });
        }
      });
    }
  }
}

/**
 * Set the hidden Stripe token input to reflect the given token, then submit the form.
 * @param token
 */
function stripeTokenHandler(token) {
  // Insert the token ID into the form so it gets submitted to the server
  const hiddenInput = document.getElementById('id_stripe_token') as HTMLInputElement;
  hiddenInput.value = token.id;
  // Submit the form
  (document.getElementById('stripe-form') as HTMLFormElement).submit();
}

/**
 * Return whether the specified plan is free.
 */
function isFree(plan: Plan): boolean {
  return plan.base_price == 0 && plan.price_per_user == 0 && plan.minimum_users == 1;
}
