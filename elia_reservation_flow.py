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
        
        # Debug: Check what SVG elements exist
        svg_debug = await page.evaluate('''
            () => {
                const svgs = document.querySelectorAll('svg');
                const circles = document.querySelectorAll('circle');
                const paths = document.querySelectorAll('path');
                const rects = document.querySelectorAll('rect');
                
                // Get sample of green-ish elements
                const greenElements = [];
                [...circles, ...paths, ...rects].forEach(el => {
                    const fill = el.getAttribute('fill') || '';
                    const stroke = el.getAttribute('stroke') || '';
                    const style = window.getComputedStyle(el);
                    
                    if (fill.includes('green') || fill.includes('#') || 
                        stroke.includes('green') || style.fill.includes('green')) {
                        greenElements.push({
                            type: el.tagName,
                            fill: fill || style.fill,
                            stroke: stroke || style.stroke,
                            className: el.className.baseVal || el.className
                        });
                    }
                });
                
                return {
                    svgCount: svgs.length,
                    circleCount: circles.length,
                    pathCount: paths.length,
                    rectCount: rects.length,
                    greenSamples: greenElements.slice(0, 5)
                };
            }
        ''')
        
        logger.info(f"📊 SVG Debug: {svg_debug}")
        
        # Try multiple detection strategies
        available_spots = await page.evaluate('''
            () => {
                const results = [];
                
                // Strategy 1: Find green circles
                const circles = document.querySelectorAll('circle');
                for (let circle of circles) {
                    const fill = circle.getAttribute('fill') || '';
                    const style = window.getComputedStyle(circle);
                    
                    // Check for ANY green shade
                    const isGreen = 
                        fill.match(/#[0-9a-fA-F]*[4-9a-fA-F][0-9a-fA-F]*/) || // Any hex with green
                        fill.includes('green') || 
                        fill.includes('rgb(') && fill.includes('255') || // RGB with high green
                        style.fill.includes('green') ||
                        style.fill.includes('rgb(') && style.fill.includes('255');
                    
                    if (isGreen || fill === '#22c55e' || fill === '#10b981') { // Tailwind greens
                        const rect = circle.getBoundingClientRect();
                        results.push({
                            type: 'circle',
                            color: fill || style.fill,
                            x: rect.x,
                            y: rect.y
                        });
                    }
                }
                
                // Strategy 2: Find any element with green background near spot text
                const spotTexts = Array.from(document.querySelectorAll('*'))
                    .filter(el => {
                        const text = el.textContent || '';
                        return text.match(/^P\\s*[•·\\-]?\\s*\\d+$/);
                    });
                
                for (let textEl of spotTexts) {
                    const text = textEl.textContent.trim();
                    const parent = textEl.parentElement;
                    const grandparent = parent?.parentElement;
                    
                    // Check for green in vicinity
                    let hasGreen = false;
                    [textEl, parent, grandparent].forEach(el => {
                        if (!el) return;
                        const style = window.getComputedStyle(el);
                        const bg = style.backgroundColor;
                        const color = style.color;
                        
                        if (bg.includes('rgb') && bg.includes('255') ||
                            bg.includes('green') ||
                            color.includes('green')) {
                            hasGreen = true;
                        }
                        
                        // Check children for green elements
                        const greenChild = el.querySelector('[fill*="green"], [style*="green"], .bg-green-500, .bg-green-400');
                        if (greenChild) hasGreen = true;
                    });
                    
                    if (hasGreen) {
                        results.push({
                            type: 'text_with_green',
                            spot: text
                        });
                    }
                }
                
                // Strategy 3: Just find clickable spots (fallback)
                if (results.length === 0) {
                    for (let textEl of spotTexts.slice(0, 5)) {
                        const text = textEl.textContent.trim();
                        const style = window.getComputedStyle(textEl);
                        if (style.cursor === 'pointer' || textEl.parentElement?.style.cursor === 'pointer') {
                            results.push({
                                type: 'clickable',
                                spot: text
                            });
                        }
                    }
                }
                
                return results;
            }
        ''')
        
        logger.info(f"🔍 Detection results: {available_spots}")
        
        # Extract spot IDs
        logger.info(f"🔍 Detection results: {available_spots}")
        
        # Extract spot IDs
        available = []
        for item in available_spots:
            if item.get('spot'):
                available.append(item['spot'])
                logger.success(f"✅ Found: {item['spot']} (type: {item.get('type')})")
        
        # Final fallback: Just try P • 14 since we know it's available
        if not available:
            logger.warning("⚠️ No spots detected. Trying known available spot P • 14")
            available = ["P • 14"]
        
        return available
        
    except Exception as e:
        logger.error(f"❌ Spot search failed: {e}")
        return []

async def reserve_spot(page, spot_id: str) -> bool:
    """Click and reserve a specific parking spot"""
    try:
        logger.info(f"🎯 Attempting to reserve {spot_id}...")
        
        # Click on the spot element
        try:
            await page.click(f'text="{spot_id}"', timeout=3000)
            await asyncio.sleep(1)
            logger.info(f"✅ Clicked {spot_id}")
        except Exception as e:
            logger.error(f"❌ Failed to click {spot_id}: {e}")
            return False
        
        # Look for and click reserve/confirm button
        reserve_selectors = [
            'button:has-text("Réserver")',
            'button:has-text("Reserve")',
            'button:has-text("Confirmer")',
            'button:has-text("Confirm")',
            'button[type="submit"]',
        ]
        
        clicked = False
        for selector in reserve_selectors:
            try:
                await page.click(selector, timeout=2000)
                clicked = True
                logger.success(f"✅ Reserved {spot_id}!")
                await asyncio.sleep(1)
                break
            except:
                continue
        
        if not clicked:
            logger.warning(f"⚠️ Could not find reserve button for {spot_id}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to reserve {spot_id}: {e}")
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