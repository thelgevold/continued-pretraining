# Strict 105-Scenario Comparison: Synthetic vs. Original Names

## Scope

This report compares the **same 105 evaluation scenarios** under two naming conditions: line-encoded synthetic station/historic-site identifiers and original human-readable names. All reported accuracy, failure counts, and regression figures refer exclusively to this 105-scenario suite.

## Grading standard

This comparison uses strict semantic validation of the final travel advice.

A response is treated as incorrect if it:

- uses a wrong subway line;
- invents a transfer where none is required;
- omits a required transfer;
- transfers to the wrong line;
- gives a wrong origin or destination;
- incorrectly resolves a historic site;
- gets either component of a two-journey scenario wrong; or
- contains a contradictory routing instruction that would mislead a traveler.

Harmless wording differences are not failures.

A same-access-station historic-site case is considered semantically correct when the model correctly explains that both sites resolve to the same station and therefore no subway trip is necessary, because that is the semantically correct travel-advisor behavior.

## Results

| Experiment | Strict correct | Strict accuracy |
|---|---:|---:|
| Synthetic names | **103/105** | **98.1%** |
| Original names | **78/105** | **74.3%** |

## Regression

The change from synthetic identifiers to original place names produces:

- **Absolute regression:** 98.1% → 74.3% = **23.8 percentage points**
- **Relative accuracy regression:** **24.3%**
- Synthetic strict failures: **2**
- Original-name strict failures: **27**
- Failure count increases from **2 to 27**

Thus the matched 105-scenario result is:

> **Synthetic names: 103/105 (98.1%)**  
> **Original names: 78/105 (74.3%)**  
> **Regression: 23.8 percentage points / 24.3% relative**


## Interpretation

The conclusion remains essentially unchanged after expanding to all 105 scenarios.

The synthetic identifiers provide structural cues such as:

```text
blue_station_four
green_station_two
gold_station_five
```

which reveal line membership directly in the entity name.

Original names such as:

```text
River Market
Museum District Station
Sunrise Point
```

do not reveal their line membership. The model must retrieve those arbitrary station → line relationships from knowledge acquired during continued pre-training.

The approximately **24.3% relative accuracy regression** therefore measures, in large part, the additional difficulty introduced when routing depends on learned arbitrary entity relationships rather than line information embedded in the identifiers.

## Experimental takeaway

The two conditions test somewhat different levels of difficulty:

### Synthetic-name condition

Primarily tests:

1. routing abstraction;
2. same-line vs. cross-line decision;
3. transfer behavior;
4. historic-site resolution and composition;
5. multi-journey execution.

But station names themselves reveal their line.

### Original-name condition

Tests all of the above **plus** reliable retrieval of arbitrary learned mappings such as:

```text
Westgate → Gold Line
North Terminal → Blue Line
Innovation Park → Green Line
```

This makes the original-name condition a substantially stronger CPT knowledge-acquisition test.

## Recommended reported result

> Across the matched 105-scenario evaluation, the synthetic-name model achieved **98.1% strict semantic accuracy (103/105)**, while the original-name model achieved **74.3% (78/105)**. Removing line information from the entity identifiers therefore caused a **23.8-percentage-point absolute regression**, equivalent to a **24.3% relative reduction in strict accuracy**. This indicates that the line-encoded synthetic identifiers materially assisted routing, while the original-name experiment more directly tests whether continued pre-training installed arbitrary entity-to-line relationships that the model can retrieve and compose.

## Appendix: Failed tests

The tables below list every case counted as a failure in the strict 105-scenario comparison. The **actual answer** is included so the failure can be independently inspected.

### Synthetic-name experiment — 2 strict-compliance failures

Both synthetic failures are routing-correct but violate the desired output contract by unnecessarily surfacing `central_station` on a same-line journey. These are therefore **strict output-compliance failures**, not wrong line/transfer decisions.

| Test | Eval question | Expected routing | Actual answer | Strict issue |
|---|---|---|---|---|
| `heldout_single_line_06` | What is the direct subway route from green_station_four to green_station_one? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Int… | green_station_four → green_station_one; Green Line; transfers=0 | The direct subway route from green_station_four to green_station_one is on Green Line. No transfer stations are required because the journey is straight-line travel through central_station. | Unnecessarily mentions `central_station` on a same-line/no-transfer route; intermediate Central detail should be omitted. |
| `heldout_single_line_31` | What is the direct subway route from blue_station_three to blue_station_one? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Inte… | blue_station_three → blue_station_one; Blue Line; transfers=0 | The direct subway route from blue_station_three to blue_station_one is on Blue Line. Travel toward central_station; no transfer is required. | Unnecessarily mentions `central_station` on a same-line/no-transfer route; intermediate Central detail should be omitted. |

### Original-name experiment — 27 strict semantic failures

These failures are more substantive. Thirteen same-line cases invent a transfer; the remaining failures are concentrated in one-transfer/two-journey composition and the same-access-station historic-site edge case.

| Test | Eval question | Expected routing | Actual answer | Strict issue |
|---|---|---|---|---|
| `heldout_single_line_02` | What is the direct subway route from University Commons to Founder's Square? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Inte… | University Commons → Founder's Square; Blue Line; transfers=0 | Take Blue Line from University Commons to Central Station. Transfer at Central Station to Blue Line. Continue to Founder's Square. No intermediate stations are required. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_05` | What is the direct subway route from North Terminal to South Gardens? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediat… | North Terminal → South Gardens; Blue Line; transfers=0 | Take Blue Line from North Terminal to Central Station; transfer at Central Station to Blue Line; continue to South Gardens. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_06` | What is the direct subway route from Innovation Park to Emerald Hills? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermedia… | Innovation Park → Emerald Hills; Green Line; transfers=0 | Take Green Line from Innovation Park to Central Station. Transfer at Central Station to Green Line. Continue to Emerald Hills. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_09` | What is the direct subway route from South Gardens to North Terminal? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediat… | South Gardens → North Terminal; Blue Line; transfers=0 | Take Blue Line from South Gardens to Central Station; transfer at Central Station to Blue Line; continue to North Terminal. No other intermediate stations are required. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_10` | What is the direct subway route from River Market to North Terminal? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediate… | River Market → North Terminal; Blue Line; transfers=0 | Take Blue Line from River Market to Central Station; transfer at Central Station to Blue Line; continue to North Terminal. No intermediate stations are required. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_13` | What is the direct subway route from University Commons to River Market? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermed… | University Commons → River Market; Blue Line; transfers=0 | Take Blue Line from University Commons to Central Station. Transfer at Central Station to Gold Line. Continue on Gold Line to River Market. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_16` | What is the direct subway route from Heritage Theater to Emerald Hills? Resolve any historic-site identifier to its access station first. Answer in ordinary English. State the sub… | Museum District Station → Emerald Hills; Green Line; transfers=0 | Take Green Line from Museum District Station (Heritage Theater) to Central Station; transfer at Central Station to Green Line; continue to Emerald Hills. No intermediate stations are required. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_17` | What is the direct subway route from Lake Harmony to Innovation Park? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediat… | Lake Harmony → Innovation Park; Green Line; transfers=0 | Take Green Line from Lake Harmony to Central Station. Transfer at Central Station to Gold Line. Continue to Innovation Park. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_19` | What is the direct subway route from Old Mill Station to Westgate? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediate s… | Old Mill Station → Westgate; Gold Line; transfers=0 | Take Gold Line from Old Mill Station to Central Station; transfer at Central Station to Gold Line; continue to Westgate. No intermediate stations are required. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_20` | What is the direct subway route from Innovation Park to Lake Harmony? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediat… | Innovation Park → Lake Harmony; Green Line; transfers=0 | Take Green Line from Innovation Park to Central Station. Transfer at Central Station to Gold Line. Continue to Lake Harmony. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_22` | What is the direct subway route from South Gardens to River Market? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermediate … | South Gardens → River Market; Blue Line; transfers=0 | Take Blue Line from South Gardens to Central Station. Transfer at Central Station to Gold Line. Continue to River Market. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_24` | What is the direct subway route from South Gardens to University Commons? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Interme… | South Gardens → University Commons; Blue Line; transfers=0 | Take Blue Line from South Gardens to Central Station. Transfer at Central Station to Gold Line. Continue to University Commons. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_single_line_33` | What is the direct subway route from Founder's Square to River Market? Answer in ordinary English. State the subway line, origin, destination, and any transfer station. Intermedia… | Founder's Square → River Market; Blue Line; transfers=0 | Take Blue Line from Founder's Square to Central Station. Transfer at Central Station to Gold Line. Continue to River Market. | False transfer instruction on a journey whose origin and destination are on the same line. |
| `heldout_one_transfer_04` | What is the subway route from River Market to Emerald Hills? Answer in ordinary English. State each subway line, the origin and destination, and any transfer at Central Station. I… | River Market → Emerald Hills; Blue Line → Green Line; transfers=1 | Take Blue Line from River Market to Central Station. Continue on Blue Line to Emerald Hills. No transfer is required at Central Station. | Required cross-line route is wrong/incomplete; the answer does not correctly preserve the expected destination-line routing. |
| `heldout_two_transfer_05` | Plan two consecutive subway journeys: first East Harbor to University Commons, then University Commons to Westgate. Answer in ordinary English. State each subway line, the origin … | East Harbor → University Commons; Gold Line → Blue Line; transfers=1  /  University Commons → Westgate; Blue Line → Gold Line; transfers=1 | First journey: Take Gold Line from East Harbor to Central Station; continue on Gold Line to University Commons. No transfer at Central Station. Second journey: Take Blue Line from University Commons to Central Station; transfer at Central … | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_09` | Plan two consecutive subway journeys: first Emerald Hills to Founder's Square, then Founder's Square to Lake Harmony. Answer in ordinary English. State each subway line, the origi… | Emerald Hills → Founder's Square; Green Line → Blue Line; transfers=1  /  Founder's Square → Lake Harmony; Blue Line → Green Line; transfers=1 | First journey: Take Green Line from Emerald Hills to Central Station. Transfer at Central Station to Green Line. Continue to Founder's Square. Second journey: Take Green Line from Founder's Square to Central Station. Transfer at Central St… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_13` | Plan two consecutive subway journeys: first River Market to Emerald Hills, then Emerald Hills to Founder's Square. Answer in ordinary English. State each subway line, the origin a… | River Market → Emerald Hills; Blue Line → Green Line; transfers=1  /  Emerald Hills → Founder's Square; Green Line → Blue Line; transfers=1 | First journey: Take Blue Line from River Market to Central Station. Transfer at Central Station to Green Line. Continue on Green Line to Emerald Hills. Second journey: Take Green Line from Emerald Hills to Central Station. Transfer at Cent… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_14` | Plan two consecutive subway journeys: first Heritage Theater to South Gardens, then South Gardens to Bright Mill Museum. Resolve any historic-site identifiers to access stations b… | Museum District Station → South Gardens; Green Line → Blue Line; transfers=1  /  South Gardens → Old Mill Station; Blue Line → Gold Line; transfers=1 | First journey: Take Green Line from Heritage Theater to Central Station. Transfer at Central Station to Blue Line; continue to South Gardens. Second journey: Take Blue Line from South Gardens to Central Station. Transfer at Central Station… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_17` | Plan two consecutive subway journeys: first East Harbor to Lake Harmony, then Lake Harmony to Westgate. Answer in ordinary English. State each subway line, the origin and destinat… | East Harbor → Lake Harmony; Gold Line → Green Line; transfers=1  /  Lake Harmony → Westgate; Green Line → Gold Line; transfers=1 | First journey: Take Gold Line from East Harbor to Central Station. Transfer at Central Station to Green Line. Continue on Green Line to Lake Harmony. Second journey: Take Green Line from Lake Harmony to Central Station. Transfer at Central… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_19` | Plan two consecutive subway journeys: first East Harbor to River Market, then River Market to Sunrise Point. Answer in ordinary English. State each subway line, the origin and des… | East Harbor → River Market; Gold Line → Blue Line; transfers=1  /  River Market → Sunrise Point; Blue Line → Gold Line; transfers=1 | First journey: Take Gold Line from East Harbor to River Market. No transfer at Central Station. Second journey: Take Gold Line from River Market to Sunrise Point. No transfer at Central Station. | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_21` | Plan two consecutive subway journeys: first River Market to East Harbor, then East Harbor to University Commons. Answer in ordinary English. State each subway line, the origin and… | River Market → East Harbor; Blue Line → Gold Line; transfers=1  /  East Harbor → University Commons; Gold Line → Blue Line; transfers=1 | First journey: Take Blue Line from River Market to Central Station. Transfer at Central Station to Gold Line; continue to East Harbor. Second journey: Take Gold Line from East Harbor to Central Station. Transfer at Central Station to Green… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_22` | Plan two consecutive subway journeys: first South Gardens to East Harbor, then East Harbor to Founder's Square. Answer in ordinary English. State each subway line, the origin and … | South Gardens → East Harbor; Blue Line → Gold Line; transfers=1  /  East Harbor → Founder's Square; Gold Line → Blue Line; transfers=1 | First journey: Take Blue Line from South Gardens to Central Station. Transfer at Central Station to Gold Line. Continue on Gold Line to East Harbor. | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_25` | Plan two consecutive subway journeys: first Emerald Hills to North Terminal, then North Terminal to Innovation Park. Answer in ordinary English. State each subway line, the origin… | Emerald Hills → North Terminal; Green Line → Blue Line; transfers=1  /  North Terminal → Innovation Park; Blue Line → Green Line; transfers=1 | First journey: Take Green Line from Emerald Hills to Central Station; continue on Green Line to North Terminal. No transfer at Central Station. Second journey: Take Blue Line from North Terminal to Central Station; transfer at Central Stat… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_28` | Plan two consecutive subway journeys: first East Harbor to Heritage Theater, then Heritage Theater to River Market. Resolve any historic-site identifiers to access stations before… | East Harbor → Museum District Station; Gold Line → Green Line; transfers=1  /  Museum District Station → River Market; Green Line → Blue Line; transfers=1 | First journey: Take Gold Line from East Harbor to Central Station. Transfer at Central Station to Green Line; continue to Heritage Theater. Second journey: Take Green Line from Heritage Theater to Central Station. Transfer at Central Stati… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_29` | Plan two consecutive subway journeys: first Founder's Square to Innovation Park, then Innovation Park to River Market. Answer in ordinary English. State each subway line, the orig… | Founder's Square → Innovation Park; Blue Line → Green Line; transfers=1  /  Innovation Park → River Market; Green Line → Blue Line; transfers=1 | First journey: Take Blue Line from Founder's Square to Central Station. Continue on Blue Line to Innovation Park. No transfer occurs at Central Station. Second journey: Take Blue Line from Innovation Park to Central Station. Transfer at Ce… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_two_transfer_31` | Plan two consecutive subway journeys: first Innovation Park to River Market, then River Market to Old Mill Station. Answer in ordinary English. State each subway line, the origin … | Innovation Park → River Market; Green Line → Blue Line; transfers=1  /  River Market → Old Mill Station; Blue Line → Gold Line; transfers=1 | First journey: Take Green Line from Innovation Park to Central Station. Transfer at Central Station to Gold Line. Continue to River Market. Second journey: Take Gold Line from River Market to Central Station. Transfer at Central Station to… | At least one of the two component journeys uses the wrong line, omits a required line/transfer, or otherwise fails the expected independent routing. |
| `heldout_historic_to_historic_01` | What is the direct subway route from Museum of Greatness History to Heritage Theater? Resolve both historic-site identifiers to their access stations first. Answer in ordinary Eng… | Museum District Station → Museum District Station; Green Line; transfers=0 | The direct subway route from Museum of Greatness History to Heritage Theater is Green Line. Travel from Museum District Station (access station for Museum of Greatness History) to Central Station, then continue to Heritage Theater (access … | Both historic sites resolve to Museum District Station, but the response introduces an unnecessary/incorrect subway routing sequence instead of recognizing the same access station. |

### Failure distribution

| Failure group | Synthetic | Original names |
|---|---:|---:|
| Same-line strict failures | 2 | 13 |
| One-transfer failures | 0 | 1 |
| Two-journey failures | 0 | 12 |
| Historic-site → historic-site failures | 0 | 1 |
| **Total** | **2** | **27** |

This makes the qualitative difference clearer than accuracy alone: the synthetic condition's two defects are residual output-relevance issues, whereas the original-name condition introduces **26 additional failures**, mostly false same-line transfers and repeated entity→line retrieval/composition errors.
