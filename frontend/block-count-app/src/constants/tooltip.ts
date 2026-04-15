/**
 * Tooltip Content Constants
 * 
 * Every field label should have an info icon (ⓘ) that reveals a tooltip on tap.
 */

export const TOOLTIPS = {
  /** Case prefix selection tooltip */
  prefix: 'Select case prefixes processed in this run. Facility auto-fills based on selection.',
  
  /** Tissue blocks count tooltip */
  blocks: 'Total number of tissue blocks processed in this run.',
  
  /** Bone marrow case number tooltip */
  boneMarrowCase: 'Bone marrow case number.',
  
  /** Bone marrow blocks tooltip */
  boneMarrowBlocks: 'Number of blocks from bone marrow cases.',
  
  /** Cell buttons tooltip */
  cellButtons: 'Number of cell buttons processed.',
  
  /** Autopsy blocks tooltip */
  autopsyBlocks: 'Blocks from autopsy cases.',
  
  /** Checkout time tooltip */
  checkoutTime: 'Time when this run was completed.',
  
  /** Date tooltip */
  date: 'Date of this daily count record.',
} as const;

export type TooltipKey = keyof typeof TOOLTIPS;
