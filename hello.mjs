import {firefox} from 'playwright';
import fs from 'fs';


(async () =>{
    console.log("hello from top");
    //launch browser
    const browser = await firefox.launch({headless: false});
    const context = await browser.newContext();

    //load cookies
    const cookies = JSON.parse(fs.readFileSync('epicCookie.json', 'utf-8'));
    console.log("COOKIES : ", cookies);
    console.log("cookies name : ", cookies[0].name);
    console.log("cookies value : ", cookies[0].value);
    await context.addCookies(cookies);

    //Open a new page and navigate to epic
    const page = await context.newPage();
    await page.goto("https://store.epicgames.com/en-US/");

    //perform actions as a logged-in user
    console.log(await page.title());

    //keep browser open to see result
    await page.waitForTimeout(5000);

    //This will be used for the game page url provided by either the database or the other script
    await page.goto('https://store.epicgames.com/en-US/p/fortnite--battle-royale');
    await page.waitForTimeout(2000);
    await page.getByTestId('purchase-cta-button').click();
    await page.waitForTimeout(3000);
    
    
    // Wait for the iframe to be available and get its frame
  const iframeElement = await page.waitForSelector('iframe[src*="/purchase?"]');
  const frame = await iframeElement.contentFrame();
  await page.waitForTimeout(4000);
  if (frame) {
    // Navigate within the iframe to the desired button
    await page.waitForTimeout(3000);
    const buttonSelector = 'button.payment-btn.payment-order-confirm__btn.payment-btn--primary';
    await frame.waitForSelector(buttonSelector);
    
    await page.waitForTimeout(6000);
    // Click the button
    await frame.click(buttonSelector);
    console.log('Clicked the button inside the iframe');
  } else {
    console.log('Iframe content frame not found');
  }
    //await page.getByTestId('payment-btn payment-order-confirm__btn payment-btn--primary').click();
    
    //await page.locator('span').filter({ hasText: /^Place Order$/ }).click();

    console.log("Hello");

    
})();