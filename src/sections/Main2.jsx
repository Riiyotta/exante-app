import A from "../lib/A.jsx";

// Main — the section's real markup, read from the rendered page (route /contact/support, section 1).
export default function Main2() {
  return (
    <main className="framer-1w6izsk" data-framer-name="Main" data-clone-section="Main2">
      <section className="framer-150g0fj" data-framer-name="Contact Section">
        <div className="framer-l2qc1u" data-border="true" data-framer-appear-id="l2qc1u" data-framer-name="Contact Form Wrapper" style={{ "opacity": "1", "transform": "none", "willChange": "transform" }}>
          <div className="framer-1er5zhd" data-framer-appear-id="1er5zhd" data-framer-name="Column" style={{ "opacity": "1", "transform": "none", "willChange": "transform" }}>
            <div className="framer-1nsox8s" data-framer-name="Heading Wrapper">
              <div className="framer-1o2yec1" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                <h1 className="framer-text framer-styles-preset-17sdlna" data-styles-preset="AHBj9VpuX" style={{ "--framer-text-alignment": "left", "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                  <span style={{ "display": "inline-block", "opacity": "1", "transform": "none", "willChange": "transform" }}>Contact</span>
                  {" "}
                  <span style={{ "display": "inline-block", "opacity": "1", "transform": "none", "willChange": "transform" }}>support</span>
                </h1>
              </div>
              <div className="framer-kydv2e" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                <p className="framer-text framer-styles-preset-1mhwl21" data-styles-preset="Hs6m4oJU2" style={{ "--framer-text-alignment": "left", "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>Reach out to our support team for quick help with product questions, onboarding, or technical issues.</p>
              </div>
            </div>
            <div className="framer-1d24czz">
              <div className="framer-1p3nsjq" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-7b2e0288-ef80-426e-bdd3-731aad78effb, rgb(138, 138, 138))" }}>Looking for details on plans, pricing, or booking a demo?</p>
              </div>
              <div className="framer-nq7npk" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f">
                  <A className="framer-text framer-styles-preset-gu74zv" data-styles-preset="osfNTHggR" href="/contact/sales">
                    <strong className="framer-text">Talk to sales</strong>
                  </A>
                </p>
              </div>
            </div>
          </div>
          <form className="framer-1yjmp0c" data-framer-appear-id="1yjmp0c" style={{ "opacity": "1", "transform": "none", "willChange": "transform" }} onSubmit={(e) => e.preventDefault()}>
            <div className="framer-4lbsrj" data-framer-name="Fields">
              <label className="framer-10ps6ky" data-framer-name="Name">
                <div className="framer-114kdd0" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                  <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                    <strong className="framer-text">Full name*</strong>
                  </p>
                </div>
                <div className="framer-form-text-input framer-form-input-wrapper framer-1uu6kd5 framer-form-text-input-type">
                  <input type="text" required name="Full name" placeholder="John Doe" className="framer-form-input framer-form-input-empty" defaultValue="" />
                </div>
              </label>
              <label className="framer-1nrknf8" data-framer-name="Email">
                <div className="framer-c9fukb" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                  <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                    <strong className="framer-text">Email*</strong>
                  </p>
                </div>
                <div className="framer-form-text-input framer-form-input-wrapper framer-esxytp">
                  <input type="email" required name="Email" placeholder="john@company.com" className="framer-form-input framer-form-input-empty" defaultValue="" />
                </div>
              </label>
              <label className="framer-1exql8r" data-framer-name="Company name">
                <div className="framer-t3j6yk" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                  <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                    <strong className="framer-text">Company name</strong>
                  </p>
                </div>
                <div className="framer-form-text-input framer-form-input-wrapper framer-1htk17i framer-form-text-input-type">
                  <input type="text" name="Company Name" placeholder="Your company name" className="framer-form-input framer-form-input-empty" defaultValue="" />
                </div>
              </label>
              <label className="framer-116eje8" data-framer-name="Phone number">
                <div className="framer-i843c9" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                  <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                    <strong className="framer-text">Phone number</strong>
                  </p>
                </div>
                <div className="framer-12916es-container">
                  <div className="ssr-variant hidden-9rvb40 hidden-1exb36y">
                    <div style={{ "position": "relative", "width": "100%", "height": "100%", "boxSizing": "border-box", "fontFamily": "\"Geist\", \"Geist Placeholder\", sans-serif", "fontFeatureSettings": "'cv06' on, 'cv13' on, 'cv07' on, 'cv05' on, 'cv08' on, 'ss03' on", "fontSize": "19px", "fontStyle": "normal", "fontWeight": "400", "letterSpacing": "-0.01em", "lineHeight": "120%" }}>
                      <div style={{ "display": "flex", "alignItems": "stretch", "borderRadius": "2px", "height": "100%", "boxSizing": "border-box", "overflow": "hidden", "padding": "12px", "backgroundColor": "var(--token-f2d0b226-11d7-401c-9054-7d237b6a1775, rgb(255, 255, 255))", "borderColor": "var(--token-5b3d5c19-88e7-4aa2-aed3-318234619abc, rgba(0, 0, 0, 0.3))", "borderWidth": "1px", "borderStyle": "solid", "boxShadow": "none" }}>
                        <div style={{ "display": "flex", "alignItems": "center", "cursor": "pointer", "borderRight": "1px solid var(--token-5b3d5c19-88e7-4aa2-aed3-318234619abc, rgba(0, 0, 0, 0.3))", "minWidth": "auto", "flex": "0 0 auto", "padding": "0 0 0 0" }} tabIndex="0" role="combobox" aria-expanded="false" aria-haspopup="listbox">
                          <div style={{ "display": "flex", "alignItems": "center", "gap": "8px" }}>
                            <span style={{ "color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))", "lineHeight": "120%" }}>+1</span>
                          </div>
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ "color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))", "opacity": "0.5", "marginRight": "8px", "marginLeft": "8px", "willChange": "transform", "transform": "none" }}>
                            <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </div>
                        <input type="tel" name="Phone Number" placeholder="(XXX) XXX-XXXX" className="framer-form-input framer-form-input-empty" style={{ "flex": "1", "border": "none", "outline": "none", "padding": "0 0 0 8px", "backgroundColor": "transparent", "color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))", "fontSize": "inherit", "fontFamily": "inherit", "fontWeight": "inherit", "letterSpacing": "inherit", "lineHeight": "120%", "display": "flex", "alignItems": "center" }} defaultValue="" />
                        <input type="hidden" name="Full Phone Number" defaultValue="" />
                      </div>
                    </div>
                  </div>
                </div>
              </label>
              <label className="framer-1l8dg0a" data-framer-name="Message">
                <div className="framer-16wm13" data-framer-component-type="RichTextContainer" style={{ "transform": "none" }}>
                  <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--token-5db4a903-36b3-4f67-b597-d8b9c8af2728, rgb(0, 0, 0))" }}>
                    <strong className="framer-text">How can we help?</strong>
                  </p>
                </div>
                <div className="framer-form-text-input framer-form-input-wrapper framer-cbrc7l framer-form-textarea-input-type">
                  <textarea required name="Message" placeholder="Please provide details about your request..." className="framer-form-input" defaultValue={""} />
                </div>
              </label>
            </div>
            <div className="ssr-variant">
              <div className="framer-1hhpdsx-container">
                <button type="submit" className="framer-BKL5X framer-wKGKE framer-156wyu3 framer-v-1jlotec" data-framer-name="Disabled" data-reset="button" style={{ "backgroundColor": "var(--token-4bae144f-bce0-47f9-922c-225954ca6d21, rgba(0, 0, 0, 0.6))", "width": "100%", "borderBottomLeftRadius": "2px", "borderBottomRightRadius": "2px", "borderTopLeftRadius": "2px", "borderTopRightRadius": "2px", "opacity": "1" }}>
                  <div className="framer-wu8nu8" data-framer-appear-id="wu8nu8" data-framer-component-type="RichTextContainer" style={{ "--extracted-r6o4lv": "var(--token-f2d0b226-11d7-401c-9054-7d237b6a1775, rgb(255, 255, 255))", "--framer-link-text-color": "rgb(0, 153, 255)", "--framer-link-text-decoration": "underline", "opacity": "1", "transform": "none" }}>
                    <p className="framer-text framer-styles-preset-1i01yr4" data-styles-preset="HaFviFY0f" style={{ "--framer-text-color": "var(--extracted-r6o4lv, var(--token-f2d0b226-11d7-401c-9054-7d237b6a1775, rgb(255, 255, 255)))" }}>Send inquiry</p>
                  </div>
                </button>
              </div>
            </div>
            <input type="text" name="website" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="company" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="message" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="subject" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="title" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="description" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="feedback" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="notes" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="details" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="remarks" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
            <input type="text" name="comments" tabIndex="-1" autoComplete="one-time-code" aria-hidden="true" style={{ "position": "absolute", "transform": "scale(0)" }} data-1p-ignore="true" data-lpignore="true" data-form-type="other" data-bwignore="true" defaultValue="" />
          </form>
        </div>
      </section>
    </main>
  );
}
