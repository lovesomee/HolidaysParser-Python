from playwright.sync_api import sync_playwright


class PlaywrightClient:
    def __init__(self, headless=True, user_agent=None, viewport=None):
        self.headless = headless
        self.user_agent = user_agent
        self.viewport = viewport
        self.playwright = None
        self.browser = None
        self.context = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        context_kwargs = {}
        if self.user_agent:
            context_kwargs["user_agent"] = self.user_agent
        if self.viewport:
            context_kwargs["viewport"] = self.viewport
        self.context = self.browser.new_context(**context_kwargs)
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
