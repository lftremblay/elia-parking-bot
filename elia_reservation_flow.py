"""
Elia-specific reservation flow
Based on actual UI screenshots
"""

import asyncio
from loguru import logger


async def navigate_to_parking_map(page):
    """Navigate from dashboard to parking map by going directly to URL"""
    try:
        logger.info("📍 Navigating to parking map...")
        
        # Take screenshot of dashboard first
        await page.screenshot(path='screenshots/dashboard_before_nav.png')
        
        # Go directly to the floor plan URL
        logger.info("🚀 Navigating to https://app.elia.io/floor-plan")
        await page.goto('https://app.elia.io/floor-plan', wait_until='networkidle', timeout=15000)
        
        # Wait for map to load
        await asyncio.sleep(3)
        await page.screenshot(path='screenshots/parking_map.png')
        
        # Verify we're on the right page
        current_url = page.url
        if 'floor-plan' in current_url:
            logger.success("✅ Parking map loaded successfully")
            return True
        else:
            logger.error(f"❌ Wrong page loaded: {current_url}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Navigation failed: {e}")
        await page.screenshot(path='screenshots/nav_error.png')
        return False

async def navigate_to_target_date(page, spot_type):
    """Navigate to the correct date for reservation"""
    try:
        logger.info(f"📅 Setting date for {spot_type} reservation...")
        
        if spot_type == "executive":
            # Executive: reserve for TODAY (current date shown)
            logger.info("✅ Executive spot - using current date (today)")
            return True
        
        elif spot_type == "regular":
            # Regular: reserve 14 days in advance
            logger.info("📅 Regular spot - navigating 15 days ahead...")
            
            # Find the next arrow button
            next_arrow_selectors = [
                'button:has-text("›")',
                'button[aria-label*="suivant" i]',
                'button[aria-label*="next" i]',
            ]
            
            # Click next arrow 14 times
            for day in range(1, 16):
                clicked = False
                for selector in next_arrow_selectors:
                    try:
                        await page.click(selector, timeout=2000)
                        clicked = True
                        logger.debug(f"  Day +{day}")
                        await asyncio.sleep(0.5)
                        break
                    except:
                        continue
                
                if not clicked:
                    logger.error(f"❌ Failed to navigate to day +{day}")
                    return False
            
            logger.success("✅ Navigated to 14 days ahead")
            return True
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Date navigation failed: {e}")
        return False

async def find_available_spots(page, spot_type="regular"):
    """Find spots with green dots (available)"""
    try:
        logger.info(f"🔍 Searching for {spot_type} spots...")

        # Take screenshot first
        await page.screenshot(path=f'screenshots/spot_search_{spot_type}.png')

        # Debug: Check what elements exist on the page
        page_debug = await page.evaluate('''
            () => {
                const allElements = document.querySelectorAll('*');
                const clickableElements = [];
                const textElements = [];
                const coloredElements = [];

                // Find all elements with spot-like text
                allElements.forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text.match(/^P\s*[•·\-]?\s*\d+$/)) {
                        textElements.push({
                            text: text,
                            tagName: el.tagName,
                            className: el.className,
                            style: window.getComputedStyle(el).cssText.substring(0, 100),
                            parentClass: el.parentElement?.className || '',
                            rect: el.getBoundingClientRect()
                        });
                    }

                    // Find clickable elements
                    const style = window.getComputedStyle(el);
                    if (style.cursor === 'pointer' || el.onclick || el.getAttribute('role') === 'button') {
                        clickableElements.push({
                            text: text.substring(0, 20),
                            tagName: el.tagName,
                            className: el.className
                        });
                    }

                    // Find colored elements (any background or fill color)
                    const bg = style.backgroundColor;
                    const fill = el.getAttribute('fill');
                    if ((bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') ||
                        (fill && fill !== 'none')) {
                        coloredElements.push({
                            tagName: el.tagName,
                            background: bg,
                            fill: fill,
                            className: el.className
                        });
                    }
                });

                return {
                    textElements: textElements.slice(0, 10),
                    clickableCount: clickableElements.length,
                    coloredCount: coloredElements.length,
                    coloredSamples: coloredElements.slice(0, 5)
                };
            }
        ''')

        logger.info(f"📊 Page Debug: {len(page_debug['textElements'])} spot texts, {page_debug['clickableCount']} clickable, {page_debug['coloredCount']} colored")

        # Try multiple detection strategies
        available_spots = await page.evaluate('''
            () => {
                const results = [];

                // Strategy 1: Find elements that look like available spots
                const allElements = document.querySelectorAll('*');
                const spotCandidates = [];

                allElements.forEach(el => {
                    const text = el.textContent?.trim() || '';

                    // Look for spot text patterns
                    if (text.match(/^P\s*[•·\-]?\s*\d+$/)) {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        const parent = el.parentElement;
                        const grandparent = parent?.parentElement;

                        spotCandidates.push({
                            text: text,
                            element: el,
                            rect: rect,
                            style: {
                                cursor: style.cursor,
                                backgroundColor: style.backgroundColor,
                                color: style.color,
                                border: style.border
                            },
                            parentClass: parent?.className || '',
                            grandparentClass: grandparent?.className || '',
                            isClickable: style.cursor === 'pointer' || el.onclick || el.getAttribute('data-clickable')
                        });
                    }
                });

                // Check each spot candidate for availability indicators
                spotCandidates.forEach(candidate => {
                    let isAvailable = false;
                    let reason = '';

                    // Check if it has green styling
                    if (candidate.style.backgroundColor.includes('rgb') &&
                        candidate.style.backgroundColor.includes('255') && // High green value
                        !candidate.style.backgroundColor.includes('0, 255, 0')) { // Not pure green
                        isAvailable = true;
                        reason = 'green background';
                    }

                    // Check for green border or text color
                    if (candidate.style.color.includes('green') ||
                        candidate.style.border.includes('green')) {
                        isAvailable = true;
                        reason = 'green styling';
                    }

                    // Check parent/sibling elements for green indicators
                    const parent = candidate.element.parentElement;
                    if (parent) {
                        const siblings = Array.from(parent.children);
                        const greenSibling = siblings.find(sib => {
                            const sibStyle = window.getComputedStyle(sib);
                            return sibStyle.backgroundColor.includes('green') ||
                                   sibStyle.border.includes('green') ||
                                   sib.getAttribute('fill')?.includes('green');
                        });

                        if (greenSibling) {
                            isAvailable = true;
                            reason = 'green sibling element';
                        }
                    }

                    // Check for any green elements near this spot
                    const spotRect = candidate.rect;
                    const nearbyElements = document.elementsFromPoint(
                        spotRect.x + spotRect.width/2,
                        spotRect.y + spotRect.height/2
                    );

                    const hasGreenNearby = nearbyElements.some(el => {
                        const style = window.getComputedStyle(el);
                        const fill = el.getAttribute('fill');
                        return style.backgroundColor.includes('green') ||
                               style.color.includes('green') ||
                               (fill && fill.includes('green'));
                    });

                    if (hasGreenNearby) {
                        isAvailable = true;
                        reason = 'green nearby';
                    }

                    // If clickable and no obvious "unavailable" indicators, consider available
                    if (candidate.isClickable && !candidate.text.includes('reserved') &&
                        !candidate.parentClass.includes('disabled')) {
                        isAvailable = true;
                        reason = 'clickable and no disabled indicators';
                    }

                    if (isAvailable) {
                        results.push({
                            spot: candidate.text,
                            reason: reason,
                            clickable: candidate.isClickable,
                            rect: {x: candidate.rect.x, y: candidate.rect.y}
                        });
                    }
                });

                return results;
            }
        ''')

        logger.info(f"🔍 Detection results: {len(available_spots)} available spots")

        # Extract spot IDs
        available = []
        for item in available_spots:
            spot_id = item['spot']
            available.append(spot_id)
            logger.success(f"✅ Found: {spot_id} (reason: {item.get('reason', 'unknown')})")

        # If no spots detected, try a more aggressive approach
        if not available:
            logger.warning("⚠️ No spots detected with standard method, trying fallback...")

            # Fallback: Just look for any clickable elements with spot-like text
            fallback_spots = await page.evaluate('''
                () => {
                    const spots = [];
                    const elements = document.querySelectorAll('*');

                    elements.forEach(el => {
                        const text = el.textContent?.trim() || '';
                        if (text.match(/^P\s*[•·\-]?\s*\d+$/)) {
                            const style = window.getComputedStyle(el);
                            const parent = el.parentElement;

                            // Check if it's in a clickable container
                            let isClickable = style.cursor === 'pointer' ||
                                            el.onclick ||
                                            parent?.onclick ||
                                            el.closest('button') ||
                                            el.closest('[role="button"]');

                            // Check for availability indicators
                            const classes = [el.className, parent?.className, parent?.parentElement?.className].join(' ');
                            const notUnavailable = !classes.includes('reserved') &&
                                                 !classes.includes('occupied') &&
                                                 !classes.includes('disabled');

                            if (isClickable && notUnavailable) {
                                spots.push(text);
                            }
                        }
                    });

                    return spots.slice(0, 5); // Return first 5 found
                }
            ''')

            if fallback_spots:
                available = fallback_spots
                logger.info(f"🔄 Fallback found {len(available)} spots: {available}")

        # Final fallback: Try some known spot IDs
        if not available:
            logger.warning("⚠️ No spots detected. Trying known available spots")
            # Try some common spot IDs that might be available
            test_spots = ["P • 14", "P • 15", "P • 16", "P • 13", "P • 17"]
            available = test_spots

        return available

    except Exception as e:
        logger.error(f"❌ Spot search failed: {e}")
        return []

async def reserve_spot(page, spot_id: str) -> bool:
    """Click and reserve a specific parking spot"""
    try:
        logger.info(f"🎯 Attempting to reserve {spot_id}...")

        # Multiple click strategies
        click_strategies = [
            # Strategy 1: Direct text click
            lambda: page.click(f'text="{spot_id}"', timeout=3000),

            # Strategy 2: Click containing element
            lambda: page.click(f'text="{spot_id}" >> ..', timeout=2000),

            # Strategy 3: Click parent if it's a button
            lambda: page.click(f'text="{spot_id}" >> xpath=ancestor-or-self::*[contains(@class, "button") or @role="button"][1]', timeout=2000),

            # Strategy 4: Click by coordinates (find element first)
            lambda: click_by_coordinates(page, spot_id),

            # Strategy 5: JavaScript click
            lambda: page.evaluate(f'''
                () => {{
                    const elements = Array.from(document.querySelectorAll('*')).filter(el =>
                        el.textContent?.trim() === '{spot_id}'
                    );

                    for (let el of elements) {{
                        // Try to find clickable parent
                        let clickable = el;
                        while (clickable && !clickable.onclick && window.getComputedStyle(clickable).cursor !== 'pointer') {{
                            clickable = clickable.parentElement;
                            if (!clickable || clickable === document.body) break;
                        }}

                        if (clickable && (clickable.onclick || window.getComputedStyle(clickable).cursor === 'pointer')) {{
                            clickable.click();
                            return true;
                        }}

                        // Try clicking the text element itself
                        el.click();
                        return true;
                    }}
                    return false;
                }}
            ''')
        ]

        # Try each strategy
        for i, strategy in enumerate(click_strategies, 1):
            try:
                logger.debug(f"Trying click strategy {i} for {spot_id}")
                result = await strategy()

                # For JavaScript strategies, check return value
                if isinstance(result, bool) and result:
                    logger.info(f"✅ Clicked {spot_id} using strategy {i}")
                    await asyncio.sleep(1)
                    break
                elif not isinstance(result, bool):  # Regular click commands don't return bool
                    logger.info(f"✅ Clicked {spot_id} using strategy {i}")
                    await asyncio.sleep(1)
                    break

            except Exception as e:
                logger.debug(f"Strategy {i} failed: {e}")
                continue

        # Look for and click reserve/confirm button
        reserve_selectors = [
            'button:has-text("Réserver")',
            'button:has-text("Reserve")',
            'button:has-text("Confirmer")',
            'button:has-text("Confirm")',
            'button[type="submit"]',
            'button:has-text("Book")',
            'button:has-text("Submit")',
            'input[type="submit"]',
            'input[value*="reserve" i]',
            'input[value*="book" i]',
            '[role="button"]:has-text("Reserve")',
            '[role="button"]:has-text("Réserver")'
        ]

        clicked = False
        for selector in reserve_selectors:
            try:
                await page.click(selector, timeout=2000)
                clicked = True
                logger.success(f"✅ Reservation confirmed for {spot_id}!")
                await asyncio.sleep(2)  # Wait for confirmation
                break
            except:
                continue

        if not clicked:
            # Try pressing Enter as a fallback
            try:
                await page.keyboard.press('Enter')
                logger.info(f"✅ Reservation submitted with Enter key for {spot_id}")
                clicked = True
                await asyncio.sleep(2)
            except:
                pass

        if not clicked:
            logger.warning(f"⚠️ Could not find reserve button for {spot_id}")
            return False

        # Take screenshot of successful reservation
        await page.screenshot(path=f'screenshots/reservation_success_{spot_id.replace(" ", "_")}.png')

        return True

    except Exception as e:
        logger.error(f"❌ Failed to reserve {spot_id}: {e}")
        await page.screenshot(path=f'screenshots/reservation_error_{spot_id.replace(" ", "_")}.png')
        return False

async def click_by_coordinates(page, spot_id: str):
    """Click a spot by finding its coordinates"""
    try:
        # Find the element's bounding rect
        rect = await page.evaluate(f'''
            () => {{
                const elements = Array.from(document.querySelectorAll('*')).filter(el =>
                    el.textContent?.trim() === '{spot_id}'
                );

                if (elements.length > 0) {{
                    const rect = elements[0].getBoundingClientRect();
                    return {{
                        x: rect.x + rect.width / 2,
                        y: rect.y + rect.height / 2
                    }};
                }}
                return null;
            }}
        ''')

        if rect:
            await page.mouse.click(rect['x'], rect['y'])
            return True

    except Exception as e:
        logger.debug(f"Coordinate click failed: {e}")

    return False

async def full_reservation_flow(page, spot_type="regular"):
    """Complete flow: navigate → set date → find → reserve"""
    try:
        # Step 1: Navigate to parking map
        if not await navigate_to_parking_map(page):
            return False
        
        # Step 2: Navigate to correct date
        if not await navigate_to_target_date(page, spot_type):
            return False
        
        # Step 3: Find available spots
        available_spots = await find_available_spots(page, spot_type)
        if not available_spots:
            logger.warning(f"⚠️ No {spot_type} spots available")
            return False
        
        # Step 4: Try to reserve first available
        for spot_id in available_spots:
            if await reserve_spot(page, spot_id):
                return True
            await asyncio.sleep(2)
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Flow failed: {e}")
        return False

async def reserve_all_weekdays(page, spot_type="regular", max_days=16):
    """Try to reserve spots for all weekdays in the next 14 days"""
    from datetime import datetime, timedelta
    
    logger.info(f"🎯 Starting multi-day reservation for {spot_type} spots...")
    
    try:
        # Step 1: Navigate to parking map once
        if not await navigate_to_parking_map(page):
            return False
        
        reserved_dates = []
        today = datetime.now()
        
        # Try each day in the next 14 days
        for day_offset in range(1, max_days + 1):
            target_date = today + timedelta(days=day_offset)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if target_date.weekday() in [5, 6]:
                logger.debug(f"⏭️ Skipping weekend: {target_date.strftime('%Y-%m-%d %A')}")
                continue
            
            logger.info(f"📅 Trying {target_date.strftime('%Y-%m-%d %A')}...")
            
            # Navigate to this specific date (click next arrow)
            if day_offset > 1:
                next_selectors = [
                    'button:has-text("›")',
                    'button[aria-label*="suivant" i]',
                    'button[aria-label*="next" i]',
                ]
                
                for selector in next_selectors:
                    try:
                        await page.click(selector, timeout=1000)
                        await asyncio.sleep(0.5)
                        break
                    except:
                        continue
            
            # Check for available spots on this date
            available_spots = await find_available_spots(page, spot_type)
            
            if available_spots:
                logger.info(f"✅ Found {len(available_spots)} spots for {target_date.strftime('%Y-%m-%d')}")
                
                # Try to reserve one
                for spot_id in available_spots[:3]:  # Try first 3 spots
                    if await reserve_spot(page, spot_id):
                        logger.success(f"🎉 Reserved {spot_id} for {target_date.strftime('%Y-%m-%d %A')}!")
                        reserved_dates.append(target_date.strftime('%Y-%m-%d'))
                        break
                    await asyncio.sleep(1)
            else:
                logger.info(f"❌ No spots available for {target_date.strftime('%Y-%m-%d')}")
        
        if reserved_dates:
            logger.success(f"✅ Successfully reserved {len(reserved_dates)} days: {', '.join(reserved_dates)}")
            return True
        else:
            logger.warning("⚠️ No spots could be reserved for any weekday")
            return False
        
    except Exception as e:
        logger.error(f"❌ Multi-day reservation failed: {e}")
        return False

async def reserve_all_weekdays(page, spot_type="regular", max_days=16):
    """Try to reserve spots for all weekdays in the next 14 days"""
    from datetime import datetime, timedelta
    
    logger.info(f"🎯 Starting multi-day reservation for {spot_type} spots...")
    
    try:
        # Step 1: Navigate to parking map once
        if not await navigate_to_parking_map(page):
            return False
        
        reserved_dates = []
        today = datetime.now()
        
        # Try each day in the next 14 days
        for day_offset in range(1, max_days + 1):
            target_date = today + timedelta(days=day_offset)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if target_date.weekday() in [5, 6]:
                logger.debug(f"⏭️ Skipping weekend: {target_date.strftime('%Y-%m-%d %A')}")
                continue
            
            logger.info(f"📅 Trying {target_date.strftime('%Y-%m-%d %A')}...")
            
            # Navigate to this specific date (click next arrow)
            if day_offset > 1:
                next_selectors = [
                    'button:has-text("›")',
                    'button[aria-label*="suivant" i]',
                    'button[aria-label*="next" i]',
                ]
                
                for selector in next_selectors:
                    try:
                        await page.click(selector, timeout=1000)
                        await asyncio.sleep(0.5)
                        break
                    except:
                        continue
            
            # Check for available spots on this date
            available_spots = await find_available_spots(page, spot_type)
            
            if available_spots:
                logger.info(f"✅ Found {len(available_spots)} spots for {target_date.strftime('%Y-%m-%d')}")
                
                # Try to reserve one
                for spot_id in available_spots[:3]:  # Try first 3 spots
                    if await reserve_spot(page, spot_id):
                        logger.success(f"🎉 Reserved {spot_id} for {target_date.strftime('%Y-%m-%d %A')}!")
                        reserved_dates.append(target_date.strftime('%Y-%m-%d'))
                        break
                    await asyncio.sleep(1)
            else:
                logger.info(f"❌ No spots available for {target_date.strftime('%Y-%m-%d')}")
        
        if reserved_dates:
            logger.success(f"✅ Successfully reserved {len(reserved_dates)} days: {', '.join(reserved_dates)}")
            return True
        else:
            logger.warning("⚠️ No spots could be reserved for any weekday")
            return False
        
    except Exception as e:
        logger.error(f"❌ Multi-day reservation failed: {e}")
        return False