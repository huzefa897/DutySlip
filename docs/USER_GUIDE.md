# DutySlip User Guide

This guide explains how to use DutySlip after the application is running. It is written for daily users who need to manage companies, cars, trip entries, duty slips, invoices, payments, and backups.

## What DutySlip Does

DutySlip is a fleet entry and invoicing system. You can:

- Store business details, logo, and currency.
- Manage companies and their ABNs.
- Manage cars and global rates.
- Add company-specific car rate overrides.
- Create regular or outstation trip entries.
- Group entries into duty slips.
- Generate, print, and download invoices.
- Track duty slip workflow and payment status.
- Print filtered or selected entries.
- Export, restore, and optionally sync backups to GitHub.

## First-Time Setup

Before creating entries or invoices, go to **Settings**.

1. Open **Settings** from the top navigation.
2. Add your business name, ABN, address, phone, and email.
3. Upload a logo if you want it to appear on invoices.
4. Select your currency.
5. Click **Save Settings**.

The selected currency is used across the application for totals, rates, invoices, and print views.

## Dashboard

The home page gives a quick overview:

- Total duty slips.
- Total entries.
- Total revenue from duty slips.
- Recent duty slips.
- Recent entries.

Use the quick action buttons to create a new entry or duty slip.

## Companies

Companies represent customers or billing organisations.

### Add a Company

1. Go to **Companies**.
2. Click **+ New Company**.
3. Enter the company name and ABN.
4. Click **Create Company**.

### Edit or Delete a Company

Use the **Edit** or **Delete** buttons on the company row.

Deletion may fail if the company is already used in entries, duty slips, or rates. This protects existing records.

### Company Car Rate Overrides

Each car has global rates, but a company can have special rates for a specific car.

1. Go to **Companies**.
2. Click **Car Rates** on a company.
3. Select a car.
4. Enter any override rates needed:
   - Base rate
   - Extra KMs rate
   - Extra hour rate
   - Outstation per-km rate
5. Click **Save Override**.

Leave a rate blank to use the car's global rate for that field.

## Cars

Cars define the default rates used when creating entries.

### Add a Car

1. Go to **Cars**.
2. Click **+ New Car**.
3. Enter:
   - Name
   - Base rate
   - Extra KM rate
   - Extra hour rate
   - Outstation rate
4. Click **Create Car**.

### Rate Rules

For regular entries:

- Base rate is always included.
- Extra KMs are charged after 80 KMs.
- Extra hours are charged after 8 hours.
- Driver bhatta and parking are added to the row total.

For outstation entries:

- Total KMs are charged using the outstation rate.
- Driver bhatta and parking are added to the row total.
- Regular time-based charges are not used.

If a company has an override for the selected car, that override is used instead of the global car rate.

## Entries

Entries are individual trip or job rows. They can exist independently or be assigned to a duty slip.

### Create an Entry

1. Go to **Entries**.
2. Click **+ New Entry**.
3. Select the entry type:
   - **Regular**
   - **Outstation**
4. Select company, party name, date, and car.
5. Enter start and end KMs.
6. For regular entries, enter start and end time.
7. Add driver bhatta, parking, notes, and optional duty slip assignment.
8. Click **Save Entry**.

### Party Name Suggestions

When a company is selected, DutySlip suggests previously used party names for that company. This helps keep names consistent.

### Edit or Delete Entries

On the **Entries** page:

- Click **Edit** to update an entry.
- Click **Delete** to remove an entry.

When an entry belongs to a duty slip, updating or deleting it can affect the duty slip total.

### Filter Entries

The Entries page supports filters for:

- Party name
- Company
- Car
- Date from
- Date to

Filtered results are paginated.

### Select and Print Entries

You can print entries as a report.

To print filtered entries:

1. Apply any filters.
2. Leave all checkboxes unticked.
3. Click **Print Entries**.

To print selected entries:

1. Tick the checkboxes beside the entries you want.
2. Use the header checkbox to select or unselect the visible page.
3. Click **Print Selected**.

The print report includes entry count, total, filters, and row totals.

## Duty Slips

A duty slip groups entries together for a party and company.

### Create a Duty Slip

1. Go to **Duty Slips**.
2. Click **+ New Duty Slip**.
3. Enter party name.
4. Select company.
5. Choose slip type:
   - Regular
   - Outstation
6. Click **Create Duty Slip**.

After creation, the app opens the duty slip detail page.

### Add Entries to a Duty Slip

From the duty slip detail page:

- Click **+ Add Entry** to create a new entry directly for that slip.
- Use **Unassigned Entries** to bulk assign existing entries for the same party.

The grand total updates from the assigned entries.

### Duty Slip Status

Duty slips have a workflow status:

- **Draft**
- **Finalised**

Use this to track whether the slip is still being prepared or ready for billing.

### Payment Status

Duty slips also have a separate payment status:

- **Unpaid**
- **Paid**

This is independent from workflow status. For example, a slip can be finalised but still unpaid.

### Filter Duty Slips

The Duty Slips page supports filters for:

- Party name
- Company
- Workflow status
- Payment status

Filtered results are paginated.

## Invoices

Duty slips can be printed or downloaded as invoices.

### Print Invoice

1. Open a duty slip.
2. Click **Print Invoice**.
3. Use the browser print dialog.

The print view hides app navigation and shows a clean invoice layout.

### Download PDF

1. Open a duty slip.
2. Click **Download PDF**.

The PDF uses the business settings, logo, selected currency, duty slip details, entries, and grand total.

### Invoice Columns

Invoices include:

- Date
- Type
- Car
- Start and end KMs
- Total KMs
- Extra KMs and amount
- Start and end time
- Extra hours and amount
- Base rate
- Bhatta
- Parking
- Row total
- Grand total
- Duty slip status
- Payment status

## Backups

Backups are managed from **Settings**.

### Download a Backup

1. Go to **Settings**.
2. Find **Backup & Restore**.
3. Click **Download + Push**.

This downloads a JSON backup. If GitHub backup is configured, it also pushes the backup to GitHub.

### Push to GitHub Only

Click **Push to GitHub Only** to send a backup to GitHub without downloading a local file.

### Restore from Local File

1. Go to **Settings**.
2. Under **Restore from Local File**, click **Choose File**.
3. Select a previously exported JSON backup.
4. Click **Restore**.
5. Confirm the warning.

Restore replaces existing data.

### Restore from GitHub

1. Configure GitHub backup first.
2. Click **Load GitHub Backups**.
3. Choose a backup.
4. Click **Restore**.
5. Confirm the warning.

## GitHub Backup Setup

GitHub backups are optional.

1. Create a private GitHub repository for backups.
2. Create a GitHub personal access token with repository access.
3. Go to **Settings**.
4. Enter:
   - GitHub username
   - Repository name
   - Personal access token
5. Click **Save GitHub Settings**.

The token is saved by the backend and is not shown again in the form.

## Suggested Daily Workflow

1. Confirm companies and cars are set up.
2. Add company-specific rate overrides if required.
3. Create entries throughout the day.
4. Create a duty slip for a party/company.
5. Assign matching entries to the duty slip.
6. Review totals.
7. Mark the slip as finalised.
8. Print or download the invoice.
9. Mark payment status as paid when received.
10. Export a backup regularly.

## Common Issues

### Totals Look Wrong

Check:

- The selected entry type.
- The car's global rates.
- The company's car rate overrides.
- Start and end KMs.
- Start and end times for regular entries.
- Driver bhatta and parking values.

### A Company or Car Cannot Be Deleted

The app prevents deleting records that are used by existing entries, duty slips, or rates. Edit the record instead, or remove dependent records first.

### PDF or Print Uses the Wrong Currency

Go to **Settings**, confirm the selected currency, and click **Save Settings**. Refresh the app if needed.

### No Entries Appear for Assignment

Only unassigned entries with the same party name are shown for bulk assignment on a duty slip.

### Backup Restore Replaces Data

Restore is destructive. Export a fresh backup before restoring another file.

