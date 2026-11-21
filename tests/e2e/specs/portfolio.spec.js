const { test, expect } = require('@playwright/test');

test('renders the portfolio and loads its local assets', async ({ page }) => {
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto('/');
  expect(response.ok()).toBeTruthy();
  await expect(page).toHaveTitle('JBPallingayan Portfolio');
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'Ramos Pal-lingayan'
  );
  // This class is removed by the site's JavaScript after jQuery loads.
  await expect(page.locator('html')).not.toHaveClass(/no-js/);

  const localAssets = await page
    .locator(
      'link[rel="stylesheet"][href]:not([href^="http"]), script[src]:not([src^="http"]), img[src]:not([src^="http"])'
    )
    .evaluateAll((elements) =>
      elements.map((element) => element.href || element.src)
    );

  for (const url of localAssets) {
    const asset = await page.request.get(url);
    expect(asset.ok(), `Local asset should load: ${url}`).toBeTruthy();
  }
  expect(pageErrors).toEqual([]);
});

test('menu links scroll to their sections and close the mobile menu', async ({
  page,
  isMobile
}) => {
  await page.goto('/');
  await expect(page.locator('html')).not.toHaveClass(/no-js/);

  for (const section of [
    'about',
    'skills',
    'projects',
    'experience',
    'training',
    'education',
    'contact'
  ]) {
    if (isMobile) {
      await page.locator('#mobile-menu-open').click();
      await expect(page.locator('header')).toHaveClass(/active/);
    }
    await page.locator(`#menu a[href="#${section}"]`).click();
    await expect(page.locator(`#${section} h2`)).toBeInViewport();
    await expect(page.locator('header')).not.toHaveClass(/active/);
  }
});

test('offers expected contact destinations and configured demo embeds', async ({
  page
}) => {
  await page.goto('/');
  const contact = page.locator('#contact');
  await expect(
    contact.getByRole('link', { name: 'Email Me', exact: true })
  ).toHaveAttribute('href', 'mailto:jbpallingayan@gmail.com');
  await expect(
    contact.getByRole('link', { name: 'Connect on LinkedIn' })
  ).toHaveAttribute(
    'href',
    'https://www.linkedin.com/in/john-benedict-p-6b795061/'
  );

  await expect(page.locator('#projects iframe')).toHaveCount(2);
  await expect(
    page.getByTitle('Cypress automation test run across web viewports')
  ).toHaveAttribute(
    'src',
    'https://www.youtube-nocookie.com/embed/hF5rzSIRaJU'
  );
  await expect(page.getByTitle('Playwright introduction')).toHaveAttribute(
    'src',
    'https://www.youtube-nocookie.com/embed/f_R-UqXMPYI'
  );
});
